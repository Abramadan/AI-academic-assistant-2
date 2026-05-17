# Progress Log

---

## 2026-05-17 — Full Application Built (v1.0)

**What was built:**

### Frontend (`frontend/index.html`)
- Complete single-page application with all 7 features
- Dark mode (default) + light mode toggle, saved to localStorage
- User authentication UI (login / register with tab toggle)
- Dashboard with 4 live stats (questions, PDFs, quizzes, tasks)
- Quick action buttons linking to all features
- Ask AI: chat-style interface with subject selector, loading indicator
- PDF Summarizer: drag-and-drop upload zone, AI summary display, copy button
- Quiz Generator: topic + count + type selector, interactive quiz UI, scoring, answer review
- Study Planner: add tasks with subject + due date, progress bar, toggle/delete
- Reminder Assistant: set reminders with datetime, overdue detection, dismiss/delete
- Toast notification system
- Responsive layout (sidebar collapses on mobile)

### Backend (`backend/app.py`)
- Flask REST API
- SQLite database with users table
- `POST /api/register` — create account with bcrypt password hashing
- `POST /api/login` — login, returns JWT token
- `GET /api/me` — get current user (JWT protected)
- `POST /api/qa` — academic Q&A using Claude claude-sonnet-4-6
- `POST /api/pdf/upload` — PDF text extraction (pdfplumber) + AI summarization
- `POST /api/quiz/generate` — AI quiz generation (multiple choice or true/false)

### Other files
- `backend/requirements.txt` — all Python dependencies
- `backend/.env.example` — environment variable template
- `docs/instructions/how-to-run.md` — full setup guide

**Next steps:**
- Get Anthropic API key and test the app end-to-end
- Add more quiz question types
- Add study planner AI suggestions
- Deploy to a web host (Render, Railway, etc.)

---

## 2026-05-17 — Project Objectives Defined

- Defined all 7 core features with full specifications
- Created `docs/project-objectives.md`
- Updated README with feature table and build order

---

## 2026-05-17 — Project Setup

- Created GitHub repository `AI-academic-assistant-2`
- Set up folder structure, README, .gitignore, docs, notes
- Copied existing frontend, initial commit pushed

---
