import os, json, io, sqlite3
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
from groq import Groq
import pdfplumber
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'change-this-secret-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
JWTManager(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'academic.db'))
FRONTEND = os.path.join(BASE_DIR, '..', 'frontend', 'index.html')

_groq = None
def get_ai():
    global _groq
    if _groq is None:
        key = os.environ.get('GROQ_API_KEY')
        if not key:
            raise RuntimeError('GROQ_API_KEY is not configured')
        _groq = Groq(api_key=key)
    return _groq

def get_db():
    db = sqlite3.connect(DB, check_same_thread=False)
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
    db.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        subject TEXT DEFAULT 'other',
        due_date TEXT,
        done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        remind_at TEXT NOT NULL,
        done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    db.commit()
    db.close()

# Called at module load — runs for both direct execution and Gunicorn
init_db()

# ── AUTH ────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Name is too long'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    db = get_db()
    user_count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if user_count >= 50:
        db.close()
        return jsonify({'error': 'Registration is closed. This app has reached its maximum capacity of 50 users.'}), 403

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                   (name, email, pw_hash))
        db.commit()
        user = db.execute('SELECT id, name, email FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        token = create_access_token(identity=str(user['id']))
        return jsonify({'token': token, 'user': dict(user)})
    except sqlite3.IntegrityError:
        db.close()
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
    if len(question) > 2000:
        return jsonify({'error': 'Question is too long (max 2000 characters)'}), 400

    ctx = f' This is a {subject} question.' if subject else ''
    try:
        prompt = (
            f'You are an expert academic tutor.{ctx} '
            f'Answer the following question clearly and accurately, '
            f'explaining concepts so the student truly understands.\n\n'
            f'Question: {question}'
        )
        response = get_ai().chat.completions.create(
            model='meta-llama/llama-4-scout-17b-16e-instruct',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return jsonify({'answer': response.choices[0].message.content})
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        err = str(e)
        if 'rate_limit' in err.lower() or '429' in err:
            return jsonify({'error': 'AI rate limit reached. Please try again in a moment.'}), 429
        return jsonify({'error': f'AI error: {err}'}), 500

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

    try:
        prompt = (
            'Please provide a comprehensive academic summary of the following text. '
            'Structure your response with these sections:\n'
            '1. Main Topic\n2. Key Concepts\n3. Important Details\n4. Conclusions\n\n'
            f'Text:\n{text[:8000]}'
        )
        response = get_ai().chat.completions.create(
            model='meta-llama/llama-4-scout-17b-16e-instruct',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return jsonify({'summary': response.choices[0].message.content, 'text': text[:5000]})
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        err = str(e)
        if 'rate_limit' in err.lower() or '429' in err:
            return jsonify({'error': 'AI rate limit reached. Please try again in a moment.'}), 429
        return jsonify({'error': f'AI error: {err}'}), 500

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
    if len(topic) > 300:
        return jsonify({'error': 'Topic is too long (max 300 characters)'}), 400

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

    try:
        response = get_ai().chat.completions.create(
            model='meta-llama/llama-4-scout-17b-16e-instruct',
            messages=[{'role': 'user', 'content': prompt}]
        )
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        err = str(e)
        if 'rate_limit' in err.lower() or '429' in err:
            return jsonify({'error': 'AI rate limit reached. Please try again in a moment.'}), 429
        return jsonify({'error': f'AI error: {err}'}), 500

    raw = response.choices[0].message.content.strip()
    if '```' in raw:
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
        raw = raw.split('```')[0]

    try:
        questions = json.loads(raw.strip())
        return jsonify({'questions': questions})
    except Exception as e:
        return jsonify({'error': f'Failed to parse quiz response: {str(e)}'}), 500

# ── PLANNER ──────────────────────────────────────────────────

@app.route('/api/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    uid = get_jwt_identity()
    db = get_db()
    rows = db.execute('SELECT * FROM tasks WHERE user_id=? ORDER BY created_at DESC', (uid,)).fetchall()
    db.close()
    return jsonify({'tasks': [dict(r) for r in rows]})

@app.route('/api/tasks', methods=['POST'])
@jwt_required()
def create_task():
    uid = get_jwt_identity()
    data = request.json or {}
    title = data.get('title', '').strip()
    subject = data.get('subject', 'other')
    due_date = data.get('due_date') or None
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if len(title) > 300:
        return jsonify({'error': 'Title is too long'}), 400
    db = get_db()
    db.execute('INSERT INTO tasks (user_id, title, subject, due_date) VALUES (?,?,?,?)',
               (uid, title, subject, due_date))
    db.commit()
    task = db.execute('SELECT * FROM tasks WHERE rowid=last_insert_rowid()').fetchone()
    db.close()
    return jsonify({'task': dict(task)}), 201

@app.route('/api/tasks/<int:tid>', methods=['PATCH'])
@jwt_required()
def update_task(tid):
    uid = get_jwt_identity()
    data = request.json or {}
    db = get_db()
    task = db.execute('SELECT * FROM tasks WHERE id=? AND user_id=?', (tid, uid)).fetchone()
    if not task:
        db.close()
        return jsonify({'error': 'Task not found'}), 404
    done = data.get('done', bool(task['done']))
    db.execute('UPDATE tasks SET done=? WHERE id=?', (int(done), tid))
    db.commit()
    updated = db.execute('SELECT * FROM tasks WHERE id=?', (tid,)).fetchone()
    db.close()
    return jsonify({'task': dict(updated)})

@app.route('/api/tasks/<int:tid>', methods=['DELETE'])
@jwt_required()
def delete_task(tid):
    uid = get_jwt_identity()
    db = get_db()
    r = db.execute('DELETE FROM tasks WHERE id=? AND user_id=?', (tid, uid))
    db.commit()
    db.close()
    if r.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'ok': True})

# ── REMINDERS ────────────────────────────────────────────────

@app.route('/api/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    uid = get_jwt_identity()
    db = get_db()
    rows = db.execute('SELECT * FROM reminders WHERE user_id=? ORDER BY remind_at ASC', (uid,)).fetchall()
    db.close()
    return jsonify({'reminders': [dict(r) for r in rows]})

@app.route('/api/reminders', methods=['POST'])
@jwt_required()
def create_reminder():
    uid = get_jwt_identity()
    data = request.json or {}
    message = data.get('message', '').strip()
    remind_at = data.get('remind_at', '').strip()
    if not message or not remind_at:
        return jsonify({'error': 'Message and remind_at are required'}), 400
    if len(message) > 500:
        return jsonify({'error': 'Message is too long'}), 400
    db = get_db()
    db.execute('INSERT INTO reminders (user_id, message, remind_at) VALUES (?,?,?)',
               (uid, message, remind_at))
    db.commit()
    rem = db.execute('SELECT * FROM reminders WHERE rowid=last_insert_rowid()').fetchone()
    db.close()
    return jsonify({'reminder': dict(rem)}), 201

@app.route('/api/reminders/<int:rid>', methods=['PATCH'])
@jwt_required()
def update_reminder(rid):
    uid = get_jwt_identity()
    data = request.json or {}
    db = get_db()
    rem = db.execute('SELECT * FROM reminders WHERE id=? AND user_id=?', (rid, uid)).fetchone()
    if not rem:
        db.close()
        return jsonify({'error': 'Reminder not found'}), 404
    done = data.get('done', bool(rem['done']))
    db.execute('UPDATE reminders SET done=? WHERE id=?', (int(done), rid))
    db.commit()
    updated = db.execute('SELECT * FROM reminders WHERE id=?', (rid,)).fetchone()
    db.close()
    return jsonify({'reminder': dict(updated)})

@app.route('/api/reminders/<int:rid>', methods=['DELETE'])
@jwt_required()
def delete_reminder(rid):
    uid = get_jwt_identity()
    db = get_db()
    r = db.execute('DELETE FROM reminders WHERE id=? AND user_id=?', (rid, uid))
    db.commit()
    db.close()
    if r.rowcount == 0:
        return jsonify({'error': 'Reminder not found'}), 404
    return jsonify({'ok': True})

# ── FRONTEND ─────────────────────────────────────────────────

@app.route('/')
def index():
    return send_file(FRONTEND)

# ── ADMIN ────────────────────────────────────────────────────

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    db.close()
    return jsonify({'registered_users': count, 'max_users': 50, 'slots_remaining': 50 - count})

# ── MAIN ─────────────────────────────────────────────────────

if __name__ == '__main__':
    print('\nAI Academic Assistant running at http://localhost:5000\n')
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, threaded=True, host='0.0.0.0', port=port)
