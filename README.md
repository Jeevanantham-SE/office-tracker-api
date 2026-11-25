Office Leave & Task Tracker API

A FastAPI + SQLAlchemy ORM backend service for managing office tasks and employee leave requests.

## Features
- **Tasks CRUD:** Create (`POST /tasks`), list/filter (`GET /tasks`), update (`PATCH /tasks/{task_id}`), and delete (`DELETE /tasks/{task_id}`) tasks.
- **Leave Requests:** Submit (`POST /leaves`), list (`GET /leaves`), and approve (`PATCH /leaves/{leave_id}/approve`) leave requests.
- **API Key Authentication:** Protected routes validated via `X-API-Key`.
- **Database & Testing:** SQLite persistence with SQLAlchemy ORM and automated tests using `pytest` and `TestClient`.

## Setup & Run
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows: .\venv\Scripts\activate
   # macOS/Linux: source venv/bin/activate


2. Install dependencies:
    pip install -r requirements.txt

3. Create a .env file based on .env.example:
    API_KEY=your-office-api-key-here
    SECRET_KEY=your-jwt-secret-key-here
    DATABASE_URL=sqlite:///./office_tracker.db

4. Start the server:
    fastapi dev main.py
    Open http://127.0.0.1:8000/docs for interactive API documentation.

5. Run automated tests:
    pytest -v

