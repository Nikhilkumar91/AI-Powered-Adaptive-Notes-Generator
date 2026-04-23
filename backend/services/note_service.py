from __future__ import annotations

from collections import Counter
import hashlib
import random
import re
from typing import Any

STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'all', 'also', 'am', 'an', 'and', 'any', 'are', 'as',
    'at', 'be', 'because', 'been', 'before', 'being', 'between', 'but', 'by', 'can', 'could',
    'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'him', 'his', 'how', 'i', 'if',
    'in', 'into', 'is', 'it', 'its', 'just', 'me', 'more', 'most', 'my', 'no', 'not', 'now', 'of',
    'on', 'once', 'only', 'or', 'other', 'our', 'out', 'over', 'own', 'same', 'she', 'should',
    'so', 'some', 'such', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these',
    'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
    'were', 'what', 'when', 'where', 'which', 'while', 'who', 'why', 'will', 'with', 'would',
    'you', 'your',
}

PRIORITY_TOPIC_PHRASES = (
    'python',
    'machine learning',
    'natural language processing',
    'deep learning',
    'artificial intelligence',
)

CANONICAL_TOPICS: list[tuple[str, tuple[str, ...]]] = [
    ('Python', ('python', 'pyhton', 'parthas')),
    ('Natural Language Processing', ('natural language processing', 'nlp', 'in lp')),
    ('Machine Learning', ('machine learning',)),
    ('Deep Learning', ('deep learning',)),
    ('Artificial Intelligence', ('artificial intelligence', 'ai')),
]

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    'Machine Learning': ('machine learning', 'supervised', 'unsupervised', 'model', 'training', 'classification', 'regression'),
    'Natural Language Processing': ('natural language processing', 'nlp', 'tokenization', 'stemming', 'lemmatization', 'pos', 'sentiment'),
    'Artificial Intelligence': ('artificial intelligence', 'ai', 'agent', 'reasoning', 'automation', 'intelligent'),
    'Deep Learning': ('deep learning', 'neural network', 'backpropagation', 'layers', 'embedding'),
    'Python': ('python', 'function', 'loop', 'list', 'dictionary', 'class', 'module'),
}

TECHNIQUE_PHRASES = (
    'segmentation',
    'tokenization',
    'tokenizing',
    'stemming',
    'lemmatization',
    'limitization',
    'part of speech tagging',
    'named entity tagging',
    'sentiment analysis',
    'stop words',
)

PHRASE_NORMALIZATION = {
    'in lp': 'nlp',
    'natural language processing': 'natural language processing',
    'machine learning': 'machine learning',
    'artificial intelligence': 'artificial intelligence',
    'deep learning': 'deep learning',
    'naive bays': 'naive bayes',
    'naive bayes': 'naive bayes',
    'limitization': 'lemmatization',
    'tokenizing': 'tokenization',
    'parthas': 'python',
    'pyhton': 'python',
}

AUTO_TOPIC_BLOCKLIST = {
    'artificial intelligence and machine learning basics',
    'artificial intelligence fundamentals',
    'artificial intelligence, machine learning, and deep learning',
    'learning notes',
    'python programming fundamentals',
    'uploaded lecture',
    'audio',
    'video',
}


def generate_notes(topic: str, transcription: str, level: str) -> dict[str, Any]:
    insight = _analyze_transcription(topic, transcription)
    level_name = _normalize_level(level)
    title = insight['topic']
    introduction = _build_introduction(insight, level_name)
    highlights = _build_highlights(insight, level_name)
    structure = _build_structure(insight, level_name)
    summary = _build_summary(insight, level_name)
    sections = _build_sections(insight, level_name)
    return {
        'topic': title,
        'title': title,
        'level': level_name,
        'introduction': introduction,
        'highlights': highlights,
        'structure': structure,
        'sections': sections,
        'summary': summary,
    }


def generate_diagrams(topic: str, transcription: str, level: str) -> list[dict[str, str]]:
    insight = _analyze_transcription(topic, transcription)
    concepts = insight['concepts'][:5] or [insight['topic']]
    flow = insight['structure_points'][:4]
    return [
        {
            'title': 'Lecture Focus',
            'type': 'Main Topic',
            'description': 'The primary topic inferred from the uploaded file.',
            'content': insight['topic'],
        },
        {
            'title': 'Concept Map',
            'type': 'Key Ideas',
            'description': 'Important ideas extracted from repeated words and strong transcript sentences.',
            'content': ' | '.join(concepts),
        },
        {
            'title': 'Study Flow',
            'type': f'{_normalize_level(level).title()} Path',
            'description': 'A learning sequence generated from this specific transcript.',
            'content': ' -> '.join(flow),
        },
    ]


def generate_quiz(topic: str, transcription: str, level: str) -> list[dict[str, Any]]:
    insight = _analyze_transcription(topic, transcription)
    difficulty = _normalize_quiz_difficulty(level)
    topic_name = insight['topic']
    lowered_topic = topic_name.lower()

    if 'natural language processing' in lowered_topic or lowered_topic == 'nlp':
        questions = _build_nlp_quiz(difficulty, insight)
        return _randomize_quiz_answer_positions(_attach_quiz_metadata(questions, insight, difficulty))
    if lowered_topic == 'python':
        questions = _build_python_quiz(difficulty, insight)
        return _randomize_quiz_answer_positions(_attach_quiz_metadata(questions, insight, difficulty))
    if 'machine learning' in lowered_topic:
        questions = _build_ml_quiz(difficulty, insight)
        return _randomize_quiz_answer_positions(_attach_quiz_metadata(questions, insight, difficulty))
    if 'artificial intelligence' in lowered_topic or lowered_topic == 'ai':
        questions = _build_ai_quiz(difficulty, insight)
        return _randomize_quiz_answer_positions(_attach_quiz_metadata(questions, insight, difficulty))
    questions = _build_generic_topic_quiz(topic_name, difficulty, insight)
    return _randomize_quiz_answer_positions(_attach_quiz_metadata(questions, insight, difficulty))


def _randomize_quiz_answer_positions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = random.SystemRandom()
    randomized: list[dict[str, Any]] = []

    for question in questions:
        options = list(question.get('options', []))
        answer_index = int(question.get('answer_index', 0))
        if not options or answer_index < 0 or answer_index >= len(options):
            randomized.append(question)
            continue

        correct_option = options[answer_index]
        distractors = [option for idx, option in enumerate(options) if idx != answer_index]
        rng.shuffle(distractors)

        # Keep correct answer in human position 2 or 3 (0-based: 1 or 2) when possible.
        target_positions = [idx for idx in (1, 2) if idx < len(options)]
        target_index = rng.choice(target_positions) if target_positions else min(1, len(options) - 1)

        new_options = list(distractors)
        new_options.insert(target_index, correct_option)

        updated = dict(question)
        updated['options'] = new_options
        updated['answer_index'] = target_index
        randomized.append(updated)

    return randomized


def _build_nlp_quiz(difficulty: str, insight: dict[str, Any]) -> list[dict[str, Any]]:
    if difficulty == 'simple':
        return [
            {
                'question': 'What is NLP mainly used for?',
                'options': [
                    'Helping computers understand human language.',
                    'Designing 3D game characters.',
                    'Repairing network cables.',
                    'Cooling computer hardware.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What does tokenization do?',
                'options': [
                    'Splits text into smaller parts like words.',
                    'Encrypts files for backup.',
                    'Changes text into images.',
                    'Optimizes CPU speed.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is a common NLP use case?',
                'options': [
                    'Chatbots and translation.',
                    'Keyboard backlight control.',
                    'Screen calibration only.',
                    'Disk partitioning only.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why do we remove stop words?',
                'options': [
                    'To reduce less useful words and keep key meaning.',
                    'To increase network latency.',
                    'To hide text from users.',
                    'To replace all nouns with verbs.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which operation finds root forms of words?',
                'options': [
                    'Stemming or lemmatization.',
                    'Image resizing.',
                    'Schema migration.',
                    'Packet routing.',
                ],
                'answer_index': 0,
            },
        ]
    if difficulty == 'difficult':
        focus = _quiz_focus_concept(insight)
        return [
            {
                'question': 'In an NLP pipeline, why is order (tokenization -> normalization -> feature extraction) important?',
                'options': [
                    'Earlier steps shape later features and model quality.',
                    'Order has no effect on learned representations.',
                    'Only feature extraction matters, preprocessing is irrelevant.',
                    'Pipeline order affects UI speed but not language performance.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'If a dataset on "{focus}" has domain-specific terms, what is the best preprocessing adjustment?',
                'options': [
                    'Tune stop words and token rules for the domain vocabulary.',
                    'Remove all rare words regardless of context.',
                    'Use only sentence length as a feature.',
                    'Convert every sentence to uppercase.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why might lemmatization outperform stemming in many production NLP tasks?',
                'options': [
                    'It preserves valid base forms and improves semantic consistency.',
                    'It always runs faster than any stemming algorithm.',
                    'It removes the need for model validation.',
                    'It guarantees perfect classification.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which metric pairing is most informative for imbalanced NLP classification?',
                'options': [
                    'Precision and recall (or F1).',
                    'Only raw accuracy.',
                    'Only training loss at epoch 1.',
                    'CPU usage and disk space.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is the strongest indicator of overfitting in NLP models?',
                'options': [
                    'Very high training performance but poor validation/test performance.',
                    'Low training and low validation performance.',
                    'Stable validation with small train-val gap.',
                    'Longer token sequences in inputs.',
                ],
                'answer_index': 0,
            },
        ]
    return [
        {
            'question': 'What is Natural Language Processing (NLP)?',
            'options': [
                'A branch of AI that helps machines understand and generate human language.',
                'A graphics engine used for game design.',
                'A database indexing technique only for SQL tables.',
                'A network protocol for sending files.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'What is tokenization in NLP?',
            'options': [
                'Breaking text into smaller units like words or sentences.',
                'Encrypting text before storage.',
                'Converting audio directly into images.',
                'Ranking web pages by popularity.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which NLP step reduces words to root form like "playing" -> "play"?',
            'options': [
                'Stemming or lemmatization.',
                'Image augmentation.',
                'Feature scaling.',
                'Database sharding.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'What does Part-of-Speech tagging do?',
            'options': [
                'Assigns grammatical labels such as noun, verb, adjective to words.',
                'Compresses large datasets into zip files.',
                'Generates random passwords for users.',
                'Creates SQL migrations automatically.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which is a common real-world use of NLP?',
            'options': [
                'Chatbots, sentiment analysis, and language translation.',
                'CPU overclocking and fan control.',
                'Building physical robot arms only.',
                'Rendering 3D animations without text.',
            ],
            'answer_index': 0,
        },
    ]


def _build_ml_quiz(difficulty: str, insight: dict[str, Any]) -> list[dict[str, Any]]:
    if difficulty == 'simple':
        return [
            {
                'question': 'What is machine learning in simple terms?',
                'options': [
                    'Learning patterns from data to make predictions.',
                    'Writing every rule manually for every case.',
                    'Only designing app colors.',
                    'A hardware cable technology.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which is a machine learning type?',
                'options': [
                    'Supervised learning.',
                    'Clipboard learning.',
                    'Cable learning.',
                    'Display learning.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why do we train an ML model?',
                'options': [
                    'So it can learn from examples and handle new data.',
                    'To avoid using data.',
                    'To store files faster.',
                    'To increase monitor brightness.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is overfitting?',
                'options': [
                    'The model memorizes training data and fails on new data.',
                    'The model has too few parameters.',
                    'The model uses cloud storage.',
                    'The model has no labels.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which metric is common for classification?',
                'options': [
                    'Accuracy.',
                    'Battery percentage.',
                    'File extension.',
                    'Fan speed.',
                ],
                'answer_index': 0,
            },
        ]
    if difficulty == 'difficult':
        focus = _quiz_focus_concept(insight)
        return [
            {
                'question': f'For ML topics centered on "{focus}", what best improves generalization?',
                'options': [
                    'Proper validation strategy, regularization, and representative data.',
                    'Increasing model complexity until training error is zero.',
                    'Evaluating only on training data.',
                    'Ignoring feature quality if model is deep enough.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'When class distribution is imbalanced, which evaluation is most reliable?',
                'options': [
                    'Precision/recall and confusion-matrix-based analysis.',
                    'Only overall accuracy.',
                    'Only number of training epochs.',
                    'Only dataset file size.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which statement about bias-variance tradeoff is correct?',
                'options': [
                    'Higher complexity can reduce bias but may increase variance.',
                    'Lower bias always means lower variance.',
                    'Variance is unrelated to model flexibility.',
                    'Tradeoff matters only for unsupervised learning.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is data leakage in ML?',
                'options': [
                    'Using information at training time that would be unavailable at prediction time.',
                    'Losing rows during CSV export.',
                    'Running out of GPU memory.',
                    'Saving a model in compressed format.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why use cross-validation?',
                'options': [
                    'To estimate stability across different train/validation splits.',
                    'To replace hyperparameter tuning entirely.',
                    'To avoid preprocessing steps.',
                    'To guarantee zero error.',
                ],
                'answer_index': 0,
            },
        ]
    # Medium difficulty: context-aware and stable-per-upload so different transcripts yield different quizzes.
    rng = _stable_quiz_rng(insight, salt='ml-medium-v1')
    concepts = [c for c in (insight.get('concepts') or []) if c]
    keywords = [k for k in (insight.get('keywords') or []) if k]
    evidence = [s for s in (insight.get('evidence_sentences') or []) if s]

    focus_a = concepts[0] if concepts else (keywords[0] if keywords else 'features')
    focus_b = concepts[1] if len(concepts) > 1 else (keywords[1] if len(keywords) > 1 else 'labels')
    scenario = evidence[0] if evidence else f'A dataset contains signals about {focus_a} and {focus_b}.'

    pool: list[dict[str, Any]] = [
        {
            'question': f'In the uploaded lecture, which best describes the learning goal when modeling "{focus_a}"?',
            'options': [
                'Learn patterns from data that generalize to new examples.',
                'Hard-code rules for every possible case.',
                'Avoid validation to save time.',
                'Use only hardware upgrades to improve results.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'Which is the best first step before training a model on {focus_a}?',
            'options': [
                'Define the target and check data quality.',
                'Deploy directly to production without testing.',
                'Remove the test set to speed up training.',
                'Choose evaluation metrics after deployment.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which evaluation is most useful when classes are imbalanced?',
            'options': [
                'Precision/recall (or F1) and a confusion matrix.',
                'Only overall accuracy.',
                'Only training loss on the last batch.',
                'Only the number of model parameters.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'Based on this context: "{scenario}" — what is data leakage?',
            'options': [
                'Using information during training that would not be available at prediction time.',
                'A CSV file being saved with fewer columns.',
                'A GPU running at high temperature.',
                'A model being exported as a zipped file.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'If your model performs well on training data but poorly on new data, what is the best explanation?',
            'options': [
                'Overfitting: the model learned training-specific noise.',
                'Underfitting: the model is too accurate.',
                'The labels are always perfect, so evaluation is wrong.',
                'Generalization improves by removing validation data.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'Which statement best matches supervised learning for "{focus_b}"?',
            'options': [
                'Training with labeled examples to predict labels for new inputs.',
                'Training with no labels and only clustering.',
                'Learning by manually typing every rule.',
                'Learning only from screen resolution settings.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'What is a reasonable train/validation/test practice?',
            'options': [
                'Keep splits separate to estimate generalization reliably.',
                'Tune hyperparameters using the test set repeatedly.',
                'Train and test on the same data to maximize accuracy.',
                'Skip a validation set because it is optional.',
            ],
            'answer_index': 0,
        },
    ]

    rng.shuffle(pool)
    return pool[:5]
    return [
        {
            'question': 'What is Machine Learning?',
            'options': [
                'A method where systems learn patterns from data to make predictions or decisions.',
                'A process to manually type rules for every scenario.',
                'Only a way to design website colors.',
                'A hardware-only technology with no data usage.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which of these is a type of machine learning?',
            'options': [
                'Supervised learning.',
                'Manual clipboard learning.',
                'Cable learning.',
                'Screen resolution learning.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'What is the goal of model training in ML?',
            'options': [
                'To learn from data so the model can generalize to new examples.',
                'To permanently store passwords in plain text.',
                'To increase video frame rate only.',
                'To avoid using any data.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which metric is commonly used for classification performance?',
            'options': [
                'Accuracy.',
                'Screen brightness.',
                'File extension.',
                'Clock speed only.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'What is overfitting in machine learning?',
            'options': [
                'When a model learns training data too specifically and performs poorly on new data.',
                'When a model is too small to run.',
                'When a model uses cloud storage.',
                'When a model has no parameters.',
            ],
            'answer_index': 0,
        },
    ]


def _build_ai_quiz(difficulty: str, insight: dict[str, Any]) -> list[dict[str, Any]]:
    if difficulty == 'simple':
        return [
            {
                'question': 'What is AI?',
                'options': [
                    'Building systems that perform intelligent tasks.',
                    'A way to print documents only.',
                    'A backup file format.',
                    'A monitor calibration tool.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which is part of AI?',
                'options': [
                    'Machine learning.',
                    'Cable management.',
                    'Manual typing.',
                    'Spreadsheet coloring.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why is data important for AI?',
                'options': [
                    'It helps models learn useful patterns.',
                    'It replaces algorithms entirely.',
                    'It is only used to rename files.',
                    'It lowers screen resolution.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'A daily life AI example is:',
                'options': [
                    'Virtual assistants and recommendations.',
                    'USB adapter size selection.',
                    'Keyboard switch type.',
                    'Static HTML pages only.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Responsible AI means:',
                'options': [
                    'Fair, safe, and transparent AI use.',
                    'Skipping tests before deployment.',
                    'Ignoring model errors.',
                    'Avoiding any monitoring.',
                ],
                'answer_index': 0,
            },
        ]
    if difficulty == 'difficult':
        focus = _quiz_focus_concept(insight)
        return [
            {
                'question': f'In AI systems focused on "{focus}", what is the best risk-control practice?',
                'options': [
                    'Monitor model behavior post-deployment and audit for bias/drift.',
                    'Evaluate only once before release.',
                    'Rely on synthetic demos instead of real validation data.',
                    'Disable feedback loops from users.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which statement best captures explainability tradeoffs?',
                'options': [
                    'Higher-performing models can be less interpretable, requiring governance controls.',
                    'Interpretability always increases with parameter count.',
                    'Black-box models remove need for human oversight.',
                    'Explainability is irrelevant outside academia.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is concept drift?',
                'options': [
                    'A change in real-world data patterns that reduces model reliability over time.',
                    'A model loading error during startup.',
                    'A temporary GPU temperature increase.',
                    'A data format conversion from JSON to CSV.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why should AI evaluation include subgroup analysis?',
                'options': [
                    'To detect uneven performance and fairness issues across populations.',
                    'To reduce the need for a test set.',
                    'To maximize only throughput.',
                    'To remove uncertainty in labels.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is a robust AI deployment pattern?',
                'options': [
                    'Staged rollout, monitoring, and rollback capability.',
                    'Immediate full rollout with no monitoring.',
                    'Model updates without versioning.',
                    'Manual score edits in production.',
                ],
                'answer_index': 0,
            },
        ]
    return [
        {
            'question': 'What is Artificial Intelligence (AI)?',
            'options': [
                'The field of creating systems that perform tasks requiring human-like intelligence.',
                'A method only for printing documents.',
                'A database backup schedule.',
                'A video codec format.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which area is a subfield of AI?',
            'options': [
                'Machine Learning.',
                'Spreadsheet coloring.',
                'Manual typing.',
                'Cable management.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which is an example of AI in daily life?',
            'options': [
                'Virtual assistants and recommendation systems.',
                'Mechanical keyboard switches.',
                'USB cable adapters.',
                'Static HTML without scripts.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Why is data important in modern AI?',
            'options': [
                'It helps models learn patterns and improve decisions.',
                'It replaces all algorithms.',
                'It is used only for naming files.',
                'It is unrelated to model quality.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which statement best describes responsible AI?',
            'options': [
                'Building fair, transparent, and safe systems with reduced bias.',
                'Ignoring errors and deployment risks.',
                'Using AI without testing.',
                'Avoiding all model monitoring.',
            ],
            'answer_index': 0,
        },
    ]


def _build_python_quiz(difficulty: str, insight: dict[str, Any]) -> list[dict[str, Any]]:
    focus = _quiz_focus_concept(insight)
    if difficulty == 'simple':
        return [
            {
                'question': 'What is Python?',
                'options': [
                    'A high-level programming language used in many domains.',
                    'A database backup format.',
                    'A hardware component.',
                    'A web browser.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Why do beginners often choose Python?',
                'options': [
                    'Its syntax is simple and readable.',
                    'It only works for experts.',
                    'It has no libraries.',
                    'It cannot run scripts.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which version should new learners generally use?',
                'options': [
                    'Python 3.x',
                    'Python 1.x',
                    'Only Python 2.0 forever',
                    'No version is needed',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Python can be used for:',
                'options': [
                    'Web development, automation, and data tasks.',
                    'Only image editing software.',
                    'Only keyboard drivers.',
                    'Only BIOS updates.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Python is commonly described as:',
                'options': [
                    'Interpreted and general-purpose.',
                    'A markup language.',
                    'A CPU architecture.',
                    'A spreadsheet plugin only.',
                ],
                'answer_index': 0,
            },
        ]
    if difficulty == 'difficult':
        return [
            {
                'question': 'Why is Python called a general-purpose language?',
                'options': [
                    'It supports many domains with broad library ecosystems.',
                    'It can only run command-line math scripts.',
                    'It is restricted to embedded firmware.',
                    'It supports only object-oriented code.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which statement about Python execution is most accurate?',
                'options': [
                    'Python is interpreted, but supports multiple programming paradigms.',
                    'Python is only procedural and cannot use objects.',
                    'Python requires manual memory allocation for every variable.',
                    'Python cannot integrate with C extensions.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is a key migration challenge from Python 2.x to 3.x?',
                'options': [
                    'Backward-incompatible syntax/runtime behavior between versions.',
                    'Python 3.x cannot import any modules.',
                    'Python 2.x has no integer type.',
                    'Python 3.x is only for web development.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'If a team uses Python for "{focus}", what best improves maintainability?',
                'options': [
                    'Clear project structure, testing, and style consistency.',
                    'Avoiding virtual environments entirely.',
                    'Skipping dependency management.',
                    'Using random scripts without modules.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'Which choice best reflects responsible Python adoption in production?',
                'options': [
                    'Version pinning, test automation, monitoring, and staged rollout.',
                    'Direct deployment without testing.',
                    'Manual edits in production only.',
                    'Ignoring package version conflicts.',
                ],
                'answer_index': 0,
            },
        ]
    return [
        {
            'question': 'Which statement best describes Python in this lecture context?',
            'options': [
                'A versatile language used across many application areas.',
                'A language only for game graphics.',
                'A tool only for database backups.',
                'A language that replaces operating systems.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Why is Python popular in education and industry?',
            'options': [
                'It is easy to learn and has strong ecosystem support.',
                'It has very limited community support.',
                'It only supports one company use case.',
                'It requires advanced hardware to start.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'Which Python version line is recommended for new learning?',
            'options': [
                '3.x',
                'Only 2.x for all new projects',
                '1.x',
                'No stable version exists',
            ],
            'answer_index': 0,
        },
        {
            'question': 'What does it mean that Python supports multiple paradigms?',
            'options': [
                'You can write procedural and object-oriented programs.',
                'You can only write GUI code.',
                'You can only write machine code.',
                'You cannot organize code into modules.',
            ],
            'answer_index': 0,
        },
        {
            'question': 'A practical first step after Python introduction is to:',
            'options': [
                'Install Python 3 and run simple scripts.',
                'Skip installation and start deployment.',
                'Use only outdated unsupported syntax.',
                'Avoid packages and standard library.',
            ],
            'answer_index': 0,
        },
    ]


def _build_generic_topic_quiz(topic_name: str, difficulty: str, insight: dict[str, Any]) -> list[dict[str, Any]]:
    if difficulty == 'simple':
        return [
            {
                'question': f'What is the main focus of {topic_name}?',
                'options': [
                    f'The core ideas explained in the uploaded lesson about {topic_name}.',
                    'Only UI color settings.',
                    'Only keyboard shortcuts.',
                    'Only hardware repair.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'How should you start learning {topic_name}?',
                'options': [
                    'Begin with basic definitions, then examples.',
                    'Memorize random answers first.',
                    'Skip concepts and jump to tests.',
                    'Ignore practical use cases.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'What helps remember {topic_name} better?',
                'options': [
                    'Review highlights and practice with simple questions.',
                    'Avoid revision completely.',
                    'Read only unrelated topics.',
                    'Skip all examples.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'A good study flow is:',
                'options': [
                    'Basics -> concepts -> applications.',
                    'Applications -> skip concepts -> random guessing.',
                    'Only summaries without details.',
                    'Only difficult exams on day one.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'Why is {topic_name} useful?',
                'options': [
                    f'It builds practical understanding of {topic_name}.',
                    'It has no practical value.',
                    'It is only about file renaming.',
                    'It is only about page formatting.',
                ],
                'answer_index': 0,
            },
        ]
    if difficulty == 'difficult':
        focus = _quiz_focus_concept(insight)
        return [
            {
                'question': f'Which review strategy best tests deep understanding of {topic_name}?',
                'options': [
                    'Explain concepts, compare alternatives, and justify tradeoffs.',
                    'Memorize definitions without context.',
                    'Read only headlines.',
                    'Skip evidence from lecture content.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'How should "{focus}" be evaluated in advanced study?',
                'options': [
                    'Assess assumptions, limitations, and practical implications.',
                    'Treat it as always valid in every scenario.',
                    'Ignore context and data quality.',
                    'Use only one anecdotal example.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'What indicates mastery of {topic_name}?',
                'options': [
                    'Ability to apply ideas to unseen problems with reasoned decisions.',
                    'Ability to recall one definition word-for-word.',
                    'Ability to list tools without explanation.',
                    'Ability to skip validation steps.',
                ],
                'answer_index': 0,
            },
            {
                'question': 'What is the strongest advanced revision habit?',
                'options': [
                    'Connect transcript evidence to frameworks and outcomes.',
                    'Ignore evidence and trust memory only.',
                    'Revise only before exams.',
                    'Avoid feedback and self-testing.',
                ],
                'answer_index': 0,
            },
            {
                'question': f'When comparing methods in {topic_name}, what matters most?',
                'options': [
                    'Context fit, constraints, performance, and risk.',
                    'Only implementation length.',
                    'Only popularity on social media.',
                    'Only visual formatting.',
                ],
                'answer_index': 0,
            },
        ]
    return [
        {
            'question': f'What best describes {topic_name}?',
            'options': [
                f'{topic_name} is the main subject explained in this lesson.',
                'It is only a browser configuration topic.',
                'It is unrelated to the uploaded learning content.',
                'It is exclusively about database backups.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'Why is {topic_name} important?',
            'options': [
                f'It provides useful concepts and practical understanding of {topic_name}.',
                'It is used only to rename files.',
                'It has no practical applications.',
                'It is only for changing UI colors.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'Which statement is relevant to {topic_name}?',
            'options': [
                f'The lesson explains key ideas and learning flow for {topic_name}.',
                'The lesson only discusses keyboard shortcuts.',
                'The lesson contains no educational content.',
                'The lesson is only a hardware assembly guide.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'What should you review first in {topic_name}?',
            'options': [
                f'The core definition and first important concept of {topic_name}.',
                'PDF page margins.',
                'Browser cache settings only.',
                'Random unrelated examples.',
            ],
            'answer_index': 0,
        },
        {
            'question': f'Which study approach is best for learning {topic_name}?',
            'options': [
                'Start with basics, then concepts, then applied examples.',
                'Skip definitions and memorize options only.',
                'Avoid practice and exercises.',
                'Focus only on UI layout.',
            ],
            'answer_index': 0,
        },
    ]


def _analyze_transcription(topic: str, transcription: str) -> dict[str, Any]:
    cleaned = _clean_text(transcription)
    sentences = _split_sentences(cleaned)
    keywords = _extract_keywords(cleaned)
    concepts = _extract_key_phrases(cleaned, keywords)
    topic_title = _resolve_topic(topic, cleaned, sentences, concepts, keywords)
    sentences = _filter_inconsistent_sentences(sentences, topic_title)
    cleaned = ' '.join(sentences) if sentences else cleaned
    keywords = _extract_keywords(cleaned)
    concepts = _extract_key_phrases(cleaned, keywords)
    evidence_sentences = _pick_evidence_sentences(sentences, keywords)
    structure_points = _derive_structure(topic_title, concepts, evidence_sentences)
    return {
        'topic': topic_title,
        'transcription': cleaned,
        'sentences': sentences,
        'keywords': keywords,
        'concepts': concepts,
        'evidence_sentences': evidence_sentences,
        'structure_points': structure_points,
    }


def _build_introduction(insight: dict[str, Any], level: str) -> str:
    topic = insight['topic']
    concepts = _join_natural(insight['concepts'][:3])
    if level == 'beginner':
        return f'This beginner note set explains {topic} in simple language using the clearest ideas detected in the uploaded file.'
    if level == 'advanced':
        if concepts:
            return f'This advanced note set studies {topic} through its main relationships: {concepts}.'
        return f'This advanced note set studies {topic} through the strongest evidence found in the transcript.'
    if concepts:
        return f'This intermediate note set organizes {topic} around the main ideas detected in the lecture: {concepts}.'
    return f'This intermediate note set organizes {topic} using the clearest transcript evidence.'


def _build_highlights(insight: dict[str, Any], level: str) -> list[str]:
    topic = insight['topic']
    concepts = set(insight['concepts'][:6])
    highlights: list[str] = []
    for sentence in insight['sentences']:
        lowered = sentence.lower()
        if topic.lower() in lowered or any(concept in lowered for concept in concepts):
            highlights.append(sentence)
        if len(highlights) >= 4:
            break

    if len(highlights) < 4:
        for sentence in insight['evidence_sentences']:
            if len(highlights) >= 4:
                break
            highlights.append(sentence)

    while len(highlights) < 4:
        if level == 'beginner':
            highlights.append(f'The main takeaway is to understand {insight["topic"]} clearly before moving deeper.')
        elif level == 'advanced':
            highlights.append(f'The lecture can be reviewed by comparing the causes, examples, and implications around {insight["topic"]}.')
        else:
            highlights.append(f'The lecture builds a practical understanding of {insight["topic"]}.')

    return _unique_keep_order(highlights)[:4]


def _build_transcript_summary(insight: dict[str, Any]) -> str:
    topic = insight['topic']
    evidence = insight['evidence_sentences'][:2]
    if evidence:
        return f'The transcript centers on {topic}. Key evidence: {" ".join(evidence)}'
    return f'The transcript centers on {topic} and provides lecture-based concepts.'


def _build_detailed_notes(insight: dict[str, Any], level: str) -> list[str]:
    notes: list[str] = []
    topic = insight['topic']
    concepts = insight['concepts'][:4]
    techniques = _extract_techniques(insight['transcription'])[:4]

    notes.append(f'Core focus: {topic}.')
    if concepts:
        notes.append(f'Primary concepts: {", ".join(concepts)}.')
    if techniques:
        notes.append(f'Techniques discussed: {", ".join(techniques)}.')
    if insight['evidence_sentences']:
        notes.append(f'Evidence from transcript: {insight["evidence_sentences"][0]}')

    while len(notes) < 4:
        if level == 'advanced':
            notes.append(f'Advanced note: evaluate how {topic} connects to outcomes and tradeoffs.')
        elif level == 'beginner':
            notes.append(f'Beginner note: revise the basics of {topic} first.')
        else:
            notes.append(f'Intermediate note: connect {topic} concepts with practical examples.')
    return notes[:4]


def _build_structure(insight: dict[str, Any], level: str) -> list[str]:
    structure = list(insight['structure_points'])
    techniques = _extract_techniques(insight['transcription'])
    topic_lower = insight['topic'].lower()
    if techniques and ('natural language processing' in topic_lower or topic_lower == 'nlp'):
        structure[2] = f'Practice the NLP pipeline in order: {", ".join(techniques[:4])}.'
    elif techniques:
        structure[2] = f'Connect the detected techniques with practical use cases: {", ".join(techniques[:4])}.'
    if level == 'beginner':
        structure[-1] = f'Simple recap: remember the easiest meaning of {insight["topic"]}.'
    elif level == 'advanced':
        structure[-1] = f'Advanced review: connect {insight["topic"]} to causes, patterns, tradeoffs, and outcomes.'
    return structure[:4]


def _build_summary(insight: dict[str, Any], level: str) -> str:
    topic = insight['topic']
    evidence = ' '.join(insight['evidence_sentences'][:2]).strip()
    concepts = _join_natural(insight['concepts'][:3])

    if level == 'beginner':
        base = f'The lecture introduces {topic} and turns the clearest spoken points into simple study notes.'
    elif level == 'advanced':
        base = f'The lecture focuses on {topic}, with attention to the relationships and implications found in the transcript.'
    else:
        base = f'The lecture focuses on {topic} and organizes the content into practical study points.'

    if concepts:
        base += f' The main detected ideas are {concepts}.'
    if evidence:
        base += f' Transcript evidence: {evidence}'
    base += ' The final notes were checked to keep topic consistency and remove irrelevant lines.'
    return base


def _build_sections(insight: dict[str, Any], level: str) -> list[dict[str, Any]]:
    topic = insight['topic']
    concepts = insight['concepts'][:4]
    evidence = insight['evidence_sentences'][:3]
    sections: list[dict[str, Any]] = [
        {
            'heading': 'Core Concepts',
            'subheading': f'What {topic} means',
            'content': [
                f'{topic} focuses on learning the main principles from the transcript evidence.',
                f'Key concepts: {", ".join(concepts)}.' if concepts else f'Key concepts are extracted directly from {topic} context.',
            ],
        },
        {
            'heading': 'Worked Example',
            'subheading': 'How to apply the idea',
            'content': [
                evidence[0] if evidence else f'Example: apply {topic} to a practical problem and evaluate the result.',
                f'Use the example to connect definition -> process -> expected outcome for {topic}.',
            ],
        },
        {
            'heading': 'Revision Points',
            'subheading': 'What to remember quickly',
            'content': _build_highlights(insight, level),
        },
    ]
    return sections


def _derive_structure(topic: str, concepts: list[str], evidence_sentences: list[str]) -> list[str]:
    first = concepts[0] if concepts else topic
    second = concepts[1] if len(concepts) > 1 else 'supporting details'
    third = concepts[2] if len(concepts) > 2 else 'important examples'
    evidence_point = evidence_sentences[0] if evidence_sentences else f'Key explanation of {topic}.'
    return [
        f'Identify the main topic: {topic}.',
        f'Understand the first important idea: {first}.',
        f'Connect {second} with {third}.',
        f'Review the clearest transcript evidence: {evidence_point}',
    ]


def _resolve_topic(
    topic: str, transcription: str, sentences: list[str], concepts: list[str], keywords: list[str]
) -> str:
    transcript_topic = _detect_topic_from_transcription(transcription)
    if transcript_topic:
        return transcript_topic
    cleaned_topic = _clean_topic(topic)
    if cleaned_topic and cleaned_topic.lower() not in AUTO_TOPIC_BLOCKLIST:
        return cleaned_topic
    prioritized_topic = _pick_priority_topic(transcription)
    if prioritized_topic:
        return prioritized_topic
    if concepts:
        return _title_from_phrase(concepts[0])
    if keywords:
        return _title_from_phrase(' '.join(keywords[:3]))
    if sentences:
        return _title_from_phrase(' '.join(_content_words(sentences[0])[:6]))
    return 'Uploaded Lecture Notes'


def _pick_priority_topic(text: str) -> str:
    lowered = (text or '').lower()
    counts = {phrase: lowered.count(phrase) for phrase in PRIORITY_TOPIC_PHRASES}
    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    if ranked and ranked[0][1] > 0:
        return _title_from_phrase(ranked[0][0])
    return ''


def _detect_topic_from_transcription(transcription: str) -> str:
    text = (transcription or '').lower()
    if not text:
        return ''
    best_label = ''
    best_score = 0
    for label, aliases in CANONICAL_TOPICS:
        score = 0
        for alias in aliases:
            score += len(re.findall(rf'\b{re.escape(alias)}\b', text))
        # Prefer topic signals that appear early in the transcript.
        early_text = text[:1200]
        for alias in aliases:
            score += 2 * len(re.findall(rf'\b{re.escape(alias)}\b', early_text))
        if score > best_score:
            best_label = label
            best_score = score
    return best_label if best_score > 0 else ''


def _normalize_phrase(text: str) -> str:
    lowered = (text or '').strip().lower()
    return PHRASE_NORMALIZATION.get(lowered, lowered)


def _extract_techniques(transcription: str) -> list[str]:
    lowered = (transcription or '').lower()
    detected: list[str] = []
    for phrase in TECHNIQUE_PHRASES:
        normalized = _normalize_phrase(phrase)
        if phrase in lowered and normalized not in detected:
            detected.append(normalized)
    return detected


def _extract_named_concepts(text: str) -> list[str]:
    lowered = (text or '').lower()
    concepts: list[str] = []
    topic = _detect_topic_from_transcription(text)
    if topic:
        concepts.append(topic.lower())
    for phrase in PRIORITY_TOPIC_PHRASES + TECHNIQUE_PHRASES:
        normalized = _normalize_phrase(phrase)
        if phrase in lowered and normalized not in concepts:
            concepts.append(normalized)
    return concepts


def _pick_evidence_sentences(sentences: list[str], keywords: list[str]) -> list[str]:
    if not sentences:
        return []
    keyword_set = set(keywords[:12])
    scored: list[tuple[int, str]] = []
    for sentence in sentences:
        words = _content_words(sentence)
        score = len(set(words) & keyword_set) * 8 + min(len(words), 24)
        if 8 <= len(sentence.split()) <= 35:
            score += 6
        scored.append((score, sentence))
    scored.sort(key=lambda item: item[0], reverse=True)
    return _unique_keep_order([sentence for _score, sentence in scored])[:4]


def _extract_keywords(text: str) -> list[str]:
    words = _content_words(text)
    counts = Counter(words)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], words.index(item[0])))
    return [word for word, count in ranked if count > 1][:12] or [word for word, _count in ranked[:12]]


def _extract_key_phrases(text: str, keywords: list[str]) -> list[str]:
    prioritized = _extract_named_concepts(text)
    phrases: Counter[str] = Counter()
    for sentence in _split_sentences(text):
        content = _content_words(sentence)
        for size in (3, 2):
            for index in range(0, max(len(content) - size + 1, 0)):
                phrase_words = content[index:index + size]
                if any(word in keywords[:12] for word in phrase_words):
                    phrase = ' '.join(phrase_words)
                    phrases[phrase] += 1

    ranked = sorted(phrases.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    selected = [phrase for phrase, _count in ranked if not _is_redundant_phrase(phrase)]
    selected = [_normalize_phrase(item) for item in selected]
    selected = [item for item in selected if not _looks_noisy_phrase(item)]
    selected = _unique_keep_order(prioritized + selected)
    if selected:
        return selected[:6]
    return [_title_from_phrase(word).lower() for word in keywords[:6]]


def _is_redundant_phrase(phrase: str) -> bool:
    words = phrase.split()
    return len(set(words)) < len(words) or all(word in STOPWORDS for word in words)


def _looks_noisy_phrase(phrase: str) -> bool:
    words = phrase.split()
    if len(words) < 2:
        return False
    noisy_starts = {'algorithm', 'understand', 'explains', 'lecture', 'came', 'now', 'talk', 'says'}
    noisy_tokens = {'came', 'picture', 'right', 'video', 'watching', 'thanks', 'bye'}
    return words[0] in noisy_starts or any(word in noisy_tokens for word in words)


def _content_words(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())
    return [word.strip("'-") for word in words if word not in STOPWORDS and len(word.strip("'-")) > 2]


def _split_sentences(text: str) -> list[str]:
    if not text:
        return []
    raw_parts = re.split(r'(?<=[.!?])\s+', text)
    return [_normalize_sentence(part) for part in raw_parts if _normalize_sentence(part)]


def _normalize_sentence(sentence: str) -> str:
    cleaned = ' '.join(sentence.split()).strip()
    cleaned = re.sub(r'\s+([,.;:!?])', r'\1', cleaned)
    if not cleaned:
        return ''
    if cleaned[-1] not in '.!?':
        cleaned += '.'
    return cleaned[:1].upper() + cleaned[1:]


def _clean_text(text: str) -> str:
    cleaned = ' '.join((text or '').replace('\r', ' ').replace('\n', ' ').split())
    cleaned = _apply_common_text_fixes(cleaned)
    cleaned = re.sub(r'\s+([,.;:!?])', r'\1', cleaned)
    sentences = _split_sentences(cleaned)
    sentences = _remove_repeated_sentences(sentences)
    cleaned = ' '.join(sentences)
    return cleaned.strip()


def _apply_common_text_fixes(text: str) -> str:
    fixed = text
    replacements = [
        (r'\bmachin learning\b', 'machine learning'),
        (r'\bdeeplearning\b', 'deep learning'),
        (r'\bpyhton\b', 'python'),
        (r'\bartifical intelligence\b', 'artificial intelligence'),
    ]
    for pattern, replacement in replacements:
        fixed = re.sub(pattern, replacement, fixed, flags=re.IGNORECASE)
    fixed = re.sub(r'\bpython is a subset of machine learning\b', 'Python is a programming language used to implement machine learning.', fixed, flags=re.IGNORECASE)
    fixed = re.sub(r'\bmachine learning is a programming language\b', 'Machine learning is a data-driven method used to build predictive models.', fixed, flags=re.IGNORECASE)
    return fixed


def _remove_repeated_sentences(sentences: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for sentence in sentences:
        key = re.sub(r'[^a-z0-9 ]+', '', sentence.lower()).strip()
        if len(key) < 8 or key in seen:
            continue
        seen.add(key)
        unique.append(sentence)
    return unique


def _filter_inconsistent_sentences(sentences: list[str], topic_title: str) -> list[str]:
    tokens = _topic_consistency_tokens(topic_title)
    if not tokens:
        return sentences
    filtered: list[str] = []
    for sentence in sentences:
        lowered = sentence.lower()
        if any(token in lowered for token in tokens):
            filtered.append(sentence)
            continue
        # Keep generally educational connective lines, drop obvious off-topic lines.
        if re.search(r'\b(example|definition|concept|model|process|application|summary)\b', lowered):
            filtered.append(sentence)
    return filtered or sentences


def _topic_consistency_tokens(topic_title: str) -> tuple[str, ...]:
    title = (topic_title or '').strip()
    for canonical, aliases in CANONICAL_TOPICS:
        if title.lower() == canonical.lower() or any(title.lower() == alias for alias in aliases):
            return TOPIC_KEYWORDS.get(canonical, ())
    return TOPIC_KEYWORDS.get(title, ())


def _clean_topic(topic: str) -> str:
    cleaned = _clean_text(topic)
    cleaned = re.sub(r'[_-]+', ' ', cleaned)
    cleaned = re.sub(r'\b\d{8,}\b', '', cleaned).strip()
    return _title_from_phrase(cleaned) if cleaned else ''


def _title_from_phrase(phrase: str) -> str:
    phrase = _clean_text(phrase)
    if not phrase:
        return ''
    small_words = {'and', 'or', 'the', 'of', 'in', 'to', 'for', 'with'}
    titled = []
    for index, word in enumerate(phrase.split()):
        lowered = word.lower()
        titled.append(lowered if index and lowered in small_words else lowered.capitalize())
    return ' '.join(titled)


def _join_natural(items: list[str]) -> str:
    clean_items = [item for item in items if item]
    if not clean_items:
        return ''
    if len(clean_items) == 1:
        return clean_items[0]
    if len(clean_items) == 2:
        return f'{clean_items[0]} and {clean_items[1]}'
    return f'{", ".join(clean_items[:-1])}, and {clean_items[-1]}'


def _normalize_level(level: str) -> str:
    return level if level in {'beginner', 'intermediate', 'advanced'} else 'intermediate'


def _normalize_quiz_difficulty(level: str) -> str:
    normalized = (level or '').strip().lower()
    mapping = {
        'simple': 'simple',
        'easy': 'simple',
        'beginner': 'simple',
        'medium': 'medium',
        'intermediate': 'medium',
        'normal': 'medium',
        'difficult': 'difficult',
        'hard': 'difficult',
        'advanced': 'difficult',
    }
    return mapping.get(normalized, 'medium')


def _quiz_focus_concept(insight: dict[str, Any]) -> str:
    concepts = insight.get('concepts') or []
    return concepts[0] if concepts else insight.get('topic', 'the topic')


def _stable_quiz_rng(insight: dict[str, Any], salt: str) -> random.Random:
    basis = (salt + '|' + str(insight.get('topic') or '') + '|' + str(insight.get('transcription') or '')).encode('utf-8', 'ignore')
    digest = hashlib.md5(basis).hexdigest()
    return random.Random(int(digest[:8], 16))


def _attach_quiz_metadata(
    questions: list[dict[str, Any]], insight: dict[str, Any], difficulty: str
) -> list[dict[str, Any]]:
    signature_basis = (
        str(insight.get('topic') or '')
        + '|'
        + difficulty
        + '|'
        + str(insight.get('transcription') or '')
    ).encode('utf-8', 'ignore')
    quiz_signature = hashlib.md5(signature_basis).hexdigest()

    enriched: list[dict[str, Any]] = []
    for question in questions:
        text = str(question.get('question') or '')
        qid = hashlib.md5((quiz_signature + '|' + text).encode('utf-8', 'ignore')).hexdigest()[:12]
        updated = dict(question)
        updated.setdefault('difficulty', difficulty)
        updated.setdefault('quiz_signature', quiz_signature)
        updated.setdefault('id', qid)
        enriched.append(updated)
    return enriched


def _unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
