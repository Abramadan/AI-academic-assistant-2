# How to Save Work to GitHub

Follow these steps every time you finish a work session.

---

## Step-by-Step

### 1. Open a terminal in the project folder
Navigate to:
```
C:\Users\CLASSIC\Desktop\AI-academic-assistant-2
```

### 2. Check what changed
```bash
git status
```
This shows all new and modified files.

### 3. Add all changes
```bash
git add .
```

### 4. Write a commit message describing what you did
```bash
git commit -m "Describe what you did here"
```
**Good examples:**
- `git commit -m "Add research notes on NLP models"`
- `git commit -m "Update frontend with new search feature"`
- `git commit -m "Add instructions for using Claude API"`

### 5. Push to GitHub
```bash
git push
```

---

## Where to Save Different Types of Work

| Type of work | Where to save |
|---|---|
| Web pages / UI code | `frontend/` |
| Python / server code | `backend/` |
| Research articles & summaries | `docs/research/` |
| How-to guides & instructions | `docs/instructions/` |
| Images, diagrams, design files | `assets/` |
| Quick notes & important info | `notes/important-info.md` |
| Daily progress | `notes/progress-log.md` |

---

## Rules

1. **Never commit API keys or passwords** — use `.env` files (they are gitignored)
2. **Always update `notes/progress-log.md`** after each session
3. **Use clear commit messages** so you can understand the history later
