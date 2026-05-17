# AI Academic Assistant 2

> A smart, AI-powered academic assistant — built to help students with research, study, writing, and learning.

---

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Objectives](#project-objectives)
- [Progress Log](#progress-log)
- [How to Save Work](#how-to-save-work)
- [Contact](#contact)

---

## About the Project

The **AI Academic Assistant** is a full-stack web application designed to support students and learners with powerful AI-driven tools. It combines AI question answering, document analysis, quiz generation, and study planning into one easy-to-use platform.

---

## Features

| # | Feature | Description | Status |
|---|---|---|---|
| 1 | User Authentication | Secure login and registration system | Planned |
| 2 | Academic Q&A | Ask any academic question, get an AI answer | Planned |
| 3 | PDF Summarization | Upload any PDF and get an instant AI summary | Planned |
| 4 | Quiz Generator | Auto-generate quizzes on any topic or text | Planned |
| 5 | Study Planner | Organize and schedule your study sessions | Planned |
| 6 | Reminder Assistant | Set reminders for study goals and deadlines | Planned |
| 7 | Dark Mode | Comfortable dark interface for night studying | Planned |

---

## Folder Structure

```
AI-academic-assistant-2/
│
├── README.md                            ← Project overview (you are here)
│
├── frontend/                            ← All web UI (HTML, CSS, JavaScript)
│   └── index.html                       ← Main web app interface
│
├── backend/                             ← Server-side code (Python)
│   └── app.py                           ← Main backend application
│
├── docs/                                ← All documentation
│   ├── project-objectives.md            ← Full feature specifications
│   ├── architecture.md                  ← System design overview
│   ├── research/                        ← Research notes and findings
│   └── instructions/                    ← Step-by-step guides
│       └── how-to-save-work.md          ← How to commit and push work
│
├── assets/                              ← Images, diagrams, design files
│
└── notes/                               ← Notes and logs
    ├── important-info.md                ← Key facts and critical information
    └── progress-log.md                  ← Daily work log
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3, Flask |
| AI Model | Claude (Anthropic API) |
| Database | SQLite |
| PDF Processing | PyPDF2 / pdfplumber |
| Auth | bcrypt + Flask-Login / JWT |
| Version Control | Git + GitHub |

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- A modern web browser (Chrome, Firefox, Edge)
- Git

### Running the Frontend
Open `frontend/index.html` directly in your browser — no server needed for UI preview.

### Running the Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

---

## Project Objectives

See the full feature-by-feature specification here:
**[docs/project-objectives.md](docs/project-objectives.md)**

### Quick Summary
1. **User Authentication** — Secure login & register with hashed passwords
2. **Academic Q&A Module** — AI-powered answers to academic questions
3. **PDF Upload & Summarization** — Upload PDFs, get structured AI summaries
4. **Quiz Generation** — Auto-generate multiple choice / T-F quizzes on any topic
5. **Study Planner** — Schedule and track study goals with AI suggestions
6. **Reminder Assistant** — In-app reminders linked to the study planner
7. **Dark Mode** — Full dark/light theme toggle saved per user

### Recommended Build Order
1. Dark Mode Interface (UI foundation)
2. User Authentication (security foundation)
3. Academic Q&A Module (core AI feature)
4. PDF Upload & Summarization
5. Quiz Generation System
6. Study Planner
7. Reminder Assistant

---

## Progress Log

See [`notes/progress-log.md`](notes/progress-log.md) for the full history of all work done.

---

## How to Save Work

Every time you finish a work session:

```bash
git add .
git commit -m "What you did"
git push
```

Full guide: [docs/instructions/how-to-save-work.md](docs/instructions/how-to-save-work.md)

---

## Contact

**Owner:** Abramadan
**GitHub:** [github.com/Abramadan](https://github.com/Abramadan)
**Email:** abramadan3554@gmail.com
