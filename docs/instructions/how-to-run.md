# How to Run the AI Academic Assistant

---

## Step 1 — Get an API Key

1. Go to https://console.anthropic.com
2. Sign in or create a free account
3. Click **API Keys** → **Create Key**
4. Copy the key (it starts with `sk-ant-...`)

---

## Step 2 — Set Up the Backend

Open a terminal and run these commands:

```bash
cd Desktop/AI-academic-assistant-2/backend

# Copy the example env file
copy .env.example .env
```

Open the `.env` file and paste your key:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
JWT_SECRET=any-long-random-string-here
```

Install Python packages:
```bash
pip install -r requirements.txt
```

Start the backend server:
```bash
python app.py
```

You should see:
```
🎓 AI Academic Assistant backend running at http://localhost:5000
```

---

## Step 3 — Open the Frontend

Open this file in your browser:
```
Desktop/AI-academic-assistant-2/frontend/index.html
```

---

## Step 4 — Create an Account

1. Click **Register**
2. Enter your name, email, and a password
3. Click **Create Account**
4. You're in!

---

## Features Available

| Feature | How to use |
|---|---|
| Ask AI | Go to "Ask AI", select a subject, type your question |
| PDF Summary | Go to "PDF Summary", drag and drop a PDF |
| Quiz | Go to "Quiz Generator", enter a topic, click Generate |
| Study Planner | Go to "Study Planner", add tasks with due dates |
| Reminders | Go to "Reminders", set a message and date/time |
| Dark Mode | Click the ☀️ button in the top-right header |

---

## Troubleshooting

**"Could not get answer"** — Backend is not running. Run `python app.py` again.

**"Invalid email or password"** — Check your credentials or register a new account.

**"Could not read PDF"** — PDF may be password-protected or image-only (no text).

**Port already in use** — Change port in `app.py`: `app.run(port=5001)` and update `API` in `index.html`.
