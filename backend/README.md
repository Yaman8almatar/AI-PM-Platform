# Backend

## Purpose
This backend exposes a real AI endpoint for generating:
- project_name
- wbs
- gantt_data
- risk_log

It integrates directly with the sibling `ai-core` module.

## Required structure
The repository root must contain:
- `backend/`
- `ai-core/`

## Setup

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
