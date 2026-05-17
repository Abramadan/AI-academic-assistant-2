# System Architecture

## Overview

The AI Academic Assistant is structured as a lightweight web application with an AI backend.

```
[ User / Browser ]
       |
       ▼
[ Frontend (HTML/CSS/JS) ]   ← index.html
       |
       ▼
[ Backend (Python / Flask) ]  ← app.py
       |
       ▼
[ AI API (Claude / OpenAI) ]
```

## Components

### Frontend
- Single-page application built with HTML, CSS, and JavaScript
- Responsive design (works on desktop and mobile)
- Communicates with backend via HTTP requests (fetch/AJAX)

### Backend
- Python-based server (Flask or similar framework)
- Handles API requests from the frontend
- Sends queries to the AI model and returns responses

### AI Layer
- Uses a language model API (e.g., Claude by Anthropic)
- Processes academic questions, research queries, and document analysis

## Data Flow

1. User types a question or uploads content in the browser
2. Frontend sends request to backend
3. Backend formats the prompt and calls the AI API
4. AI returns a response
5. Backend sends response back to frontend
6. Frontend displays the answer to the user

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3, Flask |
| AI Model | Claude (Anthropic) |
| Version Control | Git + GitHub |
| Deployment | TBD |
