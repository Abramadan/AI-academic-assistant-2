# Project Objectives

## AI Academic Assistant — Full Feature Specification

---

## Overview

The AI Academic Assistant is a full-stack web application that helps students and learners with AI-powered academic tools. The system is built around 7 core features.

---

## Feature 1: User Authentication System

**Goal:** Secure login and registration so each user has their own private space.

**Requirements:**
- User registration with name, email, and password
- Secure login with email and password
- Password hashing (never store plain passwords)
- Session management (stay logged in)
- Logout functionality
- Protected routes (only logged-in users can access features)

**Technical approach:**
- Backend: Python + Flask with `flask-login` or JWT tokens
- Passwords: Hashed with `bcrypt`
- Database: SQLite (users table: id, name, email, password_hash, created_at)

---

## Feature 2: Academic Question & Answering Module

**Goal:** Allow students to ask any academic question and get an accurate, detailed AI answer.

**Requirements:**
- Text input field for asking questions
- Subject/topic selector (Math, Science, History, Literature, etc.)
- AI-generated answers using Claude or similar model
- Answer history (saves past Q&A for review)
- Copy answer to clipboard option

**Technical approach:**
- Frontend: Chat-style interface
- Backend: API route that sends question to AI model
- AI: Claude API (`claude-sonnet-4-6` or similar)
- Storage: Save Q&A history per user in database

---

## Feature 3: PDF Upload & Summarization

**Goal:** Let students upload any PDF (textbook, paper, notes) and get an instant AI summary.

**Requirements:**
- Drag-and-drop or click-to-upload PDF interface
- File size limit (e.g. max 10MB)
- Extract text from uploaded PDF
- AI generates a structured summary (key points, main ideas)
- Option to ask follow-up questions about the PDF content
- Summary can be saved and downloaded

**Technical approach:**
- Frontend: File upload with drag-and-drop
- Backend: `PyPDF2` or `pdfplumber` to extract text
- AI: Send extracted text to Claude for summarization
- Storage: Save uploaded files and summaries per user

---

## Feature 4: Quiz Generation System

**Goal:** Automatically generate quizzes on any topic to help students test themselves.

**Requirements:**
- Select topic or paste text to generate quiz from
- Choose number of questions (5, 10, 15, 20)
- Choose question type (multiple choice, true/false, short answer)
- AI generates the quiz
- Interactive quiz-taking interface (select answer, submit)
- Score shown at the end with correct answers explained
- Save quiz history

**Technical approach:**
- Frontend: Quiz UI with selectable answer options
- Backend: AI prompt engineering to generate structured quiz JSON
- AI: Claude generates questions + answer options + correct answer + explanation
- Storage: Save quiz results per user

---

## Feature 5: Study Planner

**Goal:** Help students organize their study schedule and track what they need to study.

**Requirements:**
- Add subjects / topics to study
- Set study goals (e.g. "Finish Chapter 3 by Friday")
- Calendar or list view of study schedule
- Mark tasks as complete
- AI suggests a study plan based on subjects and available time
- Progress tracking (% complete)

**Technical approach:**
- Frontend: Calendar + task list UI
- Backend: CRUD routes for study tasks (create, read, update, delete)
- AI: Generates a suggested schedule when user inputs subjects + deadline
- Storage: Study tasks table in database (id, user_id, subject, goal, due_date, completed)

---

## Feature 6: Reminder Assistant

**Goal:** Send reminders to help students stay on track with their study goals.

**Requirements:**
- Set reminders for study sessions, assignment deadlines, quiz reviews
- Reminder types: in-app notifications
- View all upcoming reminders
- Mark reminders as done
- AI can suggest reminder times based on study plan

**Technical approach:**
- Frontend: Reminders list with notification badges
- Backend: Reminders table in database (id, user_id, message, remind_at, is_done)
- Notification: Browser notification API or in-app alert system
- Integration: Linked to Study Planner (auto-create reminders from study tasks)

---

## Feature 7: Dark Mode Interface

**Goal:** Comfortable reading experience, especially for night-time studying.

**Requirements:**
- Toggle switch between light mode and dark mode
- Dark mode saves user preference (stays dark after refresh)
- All pages and components support both modes
- Smooth transition animation when switching
- Default: dark mode (easier on eyes for studying)

**Technical approach:**
- CSS custom properties (variables) for all colors
- JavaScript toggle that adds/removes a `.dark` class on `<body>`
- `localStorage` saves the user's preference
- Transition: `transition: background 0.3s ease`

---

## Summary Table

| # | Feature | Priority | Status |
|---|---|---|---|
| 1 | User Authentication (Login/Register) | High | Planned |
| 2 | Academic Q&A Module | High | Planned |
| 3 | PDF Upload & Summarization | High | Planned |
| 4 | Quiz Generation System | Medium | Planned |
| 5 | Study Planner | Medium | Planned |
| 6 | Reminder Assistant | Medium | Planned |
| 7 | Dark Mode Interface | High | Planned |

---

## Development Order (Recommended)

Build in this order for the smoothest development experience:

1. **Dark Mode Interface** — set up first so all future UI looks right
2. **User Authentication** — must exist before anything else is user-specific
3. **Academic Q&A Module** — core AI feature, builds confidence in AI integration
4. **PDF Upload & Summarization** — extends the AI integration
5. **Quiz Generation System** — builds on Q&A and PDF features
6. **Study Planner** — standalone productivity feature
7. **Reminder Assistant** — integrates with Study Planner at the end

---

*Document created: May 2026*
*Last updated: May 2026*
