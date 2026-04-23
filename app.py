from dotenv import load_dotenv
import os

load_dotenv('env')

from backend.app import app

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=int(os.getenv('PORT', '5000')),
        debug=True,
        use_reloader=False,
    )
