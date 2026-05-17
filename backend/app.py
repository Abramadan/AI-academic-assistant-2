import os, json, io, sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
from anthropic import Anthropic
import pdfplumber
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'change-this-secret-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
JWTManager(app)

ai = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

DB = 'academic.db'

def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    db.close()

# ── AUTH ────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        db = get_db()
        db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                   (name, email, pw_hash))
        db.commit()
        user = db.execute('SELECT id, name, email FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        token = create_access_token(identity=str(user['id']))
        return jsonify({'token': token, 'user': dict(user)})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    db.close()

    if not user or not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_access_token(identity=str(user['id']))
    return jsonify({'token': token, 'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}})

@app.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    uid = get_jwt_identity()
    db = get_db()
    user = db.execute('SELECT id, name, email FROM users WHERE id = ?', (uid,)).fetchone()
    db.close()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': dict(user)})

# ── Q&A ─────────────────────────────────────────────────────

@app.route('/api/qa', methods=['POST'])
@jwt_required()
def qa():
    data = request.json or {}
    question = data.get('question', '').strip()
    subject = data.get('subject', '')
    if not question:
        return jsonify({'error': 'Question is required'}), 400

    ctx = f' This is a {subject} question.' if subject else ''
    msg = ai.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=1024,
        messages=[{
            'role': 'user',
            'content': (
                f'You are an expert academic tutor.{ctx} '
                f'Answer the following question clearly and accurately, '
                f'explaining concepts so the student truly understands.\n\n'
                f'Question: {question}'
            )
        }]
    )
    return jsonify({'answer': msg.content[0].text})

# ── PDF ─────────────────────────────────────────────────────

@app.route('/api/pdf/upload', methods=['POST'])
@jwt_required()
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    if not f.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are accepted'}), 400

    pdf_bytes = io.BytesIO(f.read())
    text = ''
    try:
        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages[:25]:
                text += (page.extract_text() or '') + '\n'
    except Exception:
        return jsonify({'error': 'Could not read PDF. Make sure it is not password protected.'}), 400

    if not text.strip():
        return jsonify({'error': 'Could not extract text from this PDF'}), 400

    msg = ai.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=1500,
        messages=[{
            'role': 'user',
            'content': (
                'Please provide a comprehensive academic summary of the following text. '
                'Structure your response with these sections:\n'
                '1. Main Topic\n2. Key Concepts\n3. Important Details\n4. Conclusions\n\n'
                f'Text:\n{text[:8000]}'
            )
        }]
    )
    return jsonify({'summary': msg.content[0].text, 'text': text[:5000]})

# ── QUIZ ─────────────────────────────────────────────────────

@app.route('/api/quiz/generate', methods=['POST'])
@jwt_required()
def generate_quiz():
    data = request.json or {}
    topic = data.get('topic', '').strip()
    count = min(int(data.get('count', 10)), 20)
    qtype = data.get('type', 'multiple_choice')

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    if qtype == 'true_false':
        fmt = 'Each question is a statement that is True or False. Options must be exactly ["True", "False"].'
    else:
        fmt = 'Each question has exactly 4 answer options.'

    prompt = (
        f'Generate {count} quiz questions about: {topic}\n\n'
        f'{fmt}\n\n'
        'Return ONLY a valid JSON array — no other text, no markdown fences:\n'
        '[\n'
        '  {\n'
        '    "question": "Question text?",\n'
        '    "options": ["A", "B", "C", "D"],\n'
        '    "correct_index": 0,\n'
        '    "explanation": "Why this answer is correct."\n'
        '  }\n'
        ']\n\n'
        'correct_index is the 0-based index of the correct answer.'
    )

    msg = ai.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=3000,
        messages=[{'role': 'user', 'content': prompt}]
    )

    raw = msg.content[0].text.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
        raw = raw.split('```')[0]

    questions = json.loads(raw.strip())
    return jsonify({'questions': questions})

# ── MAIN ─────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print('\n🎓 AI Academic Assistant backend running at http://localhost:5000\n')
    app.run(debug=True, port=5000)
