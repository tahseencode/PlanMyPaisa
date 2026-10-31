# PlanMyPaisa

A small app for submitting financial transactions and processing them in the background. Flask handles the API, Celery does the actual work, and a React frontend polls for the result, so the page never hangs while a transaction is being processed.

## Stack

- Backend: Flask
- Background jobs: Celery with Redis as the broker
- Frontend: React, React Three Fiber, Framer Motion

## Project structure

```
.
├── app.py            # Flask app and API routes
├── tasks.py          # Celery app and tasks
├── app.js            # Root React component
├── templates/        # index.html
├── static/css/       # style.css
├── package.json
└── requirements.txt
```

## Getting started

You'll need Python 3.8+, Node.js, and Redis.

```bash
git clone <your-repository-url>
cd PlanMyPaisa

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
npm install
```

Redis doesn't officially support Windows. If you're on Windows, grab the [community port](https://github.com/tporadowski/redis/releases) and tick the "Add to PATH" option during install.

## Running it

Open four terminals (activate the venv in the Python ones):

```bash
redis-server                              # 1. Redis
celery -A tasks.app worker --loglevel=info  # 2. Celery worker
python app.py                             # 3. Flask API on :5000
npm start                                 # 4. React app on :3000
```

On Windows, if PowerShell blocks scripts, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

## API

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/health` | Health check |
| POST | `/transactions` | Queue a transaction, returns a `task_id` (202) |
| GET | `/tasks/<task_id>` | Get the task's status and result |

Example request to `/transactions`:

```json
{
  "customer_id": "CUST-12345",
  "amount": 4.50,
  "description": "Morning coffee at Starbucks"
}
```

## Note

This is a demo project, not production-ready. MIT license.
