from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError


class MongoRepository:
    def __init__(self, uri: str, database_name: str) -> None:
        self._uri = uri
        self._database_name = database_name
        self._client: MongoClient | None = None
        self._db = None
        self._error: str | None = None
        self._connect()

    def _connect(self) -> None:
        try:
            self._client = MongoClient(self._uri, serverSelectionTimeoutMS=2000)
            self._client.admin.command('ping')
            self._db = self._client[self._database_name]
            self._db.note_sessions.create_index([('created_at', -1)])
            self._db.note_sessions.create_index('topic')
            self._db.users.create_index('email', unique=True)
            self._db.users.create_index([('created_at', -1)])
            self._error = None
        except PyMongoError as exc:
            self._client = None
            self._db = None
            self._error = str(exc)

    @property
    def is_connected(self) -> bool:
        return self._db is not None

    @property
    def error(self) -> str | None:
        return self._error

    def create_session(self, payload: dict[str, Any]) -> str | None:
        if self._db is None:
            return None
        document = {
            **payload,
            'exports': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        result = self._db.note_sessions.insert_one(document)
        return str(result.inserted_id)

    def attach_export(self, session_id: str, export_data: dict[str, Any]) -> bool:
        if self._db is None:
            return False
        result = self._db.note_sessions.update_one(
            {'_id': self._to_object_id(session_id)},
            {
                '$push': {'exports': export_data},
                '$set': {'updated_at': datetime.utcnow()},
            },
        )
        return result.modified_count > 0

    def list_history(self) -> list[dict[str, Any]]:
        if self._db is None:
            return []
        items: list[dict[str, Any]] = []
        cursor = self._db.note_sessions.find({}, sort=[('created_at', -1)])
        for doc in cursor:
            exports = doc.get('exports', [])
            latest_export = exports[-1] if exports else None
            items.append(
                {
                    'id': str(doc['_id']),
                    'topic': doc.get('topic', 'Learning Notes'),
                    'level': doc.get('level', 'intermediate'),
                    'source_filename': doc.get('source_filename', ''),
                    'transcription': doc.get('transcription', ''),
                    'notes': doc.get('notes', {}),
                    'created_at': self._iso(doc.get('created_at')),
                    'updated_at': self._iso(doc.get('updated_at')),
                    'latest_export': latest_export,
                    'exports': exports,
                }
            )
        return items

    def delete_session(self, session_id: str) -> bool:
        if self._db is None:
            return False
        result = self._db.note_sessions.delete_one({'_id': self._to_object_id(session_id)})
        return result.deleted_count > 0

    def create_user(self, payload: dict[str, Any]) -> str | None:
        if self._db is None:
            return None
        document = {
            **payload,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        try:
            result = self._db.users.insert_one(document)
        except DuplicateKeyError:
            return None
        return str(result.inserted_id)

    def find_user_by_email(self, email: str) -> dict[str, Any] | None:
        if self._db is None:
            return None
        doc = self._db.users.find_one({'email': email})
        if not doc:
            return None
        return {
            'id': str(doc['_id']),
            'email': doc.get('email'),
            'password_hash': doc.get('password_hash'),
            'name': doc.get('name'),
            'created_at': self._iso(doc.get('created_at')),
        }

    def _to_object_id(self, value: str):
        from bson import ObjectId

        return ObjectId(value)

    @staticmethod
    def _iso(value: Any) -> str | None:
        if isinstance(value, datetime):
            return value.isoformat()
        return None
