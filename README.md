# Health Habit Tracker (Prototype)

This is a minimal Flask application demonstrating how one might upload Apple Health XML data,
create daily habits, and store entries.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

The server listens on `http://localhost:5000`.

## Endpoints

- `POST /upload` – upload an Apple Health XML file (`file` field in form-data).
- `POST /habits` – create a habit. JSON body with `name` and `input_type`.
- `POST /habit_entries` – add an entry. JSON body with `habit_id`, `entry_date` (YYYY-MM-DD), and `value`.
- `GET /analytics` – placeholder endpoint for analytics.

Uploaded files are stored in the `uploads/` directory, and a simple SQLite database is created as `app.db`.
