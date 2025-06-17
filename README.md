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

## Beginner Guide

The steps above assume some familiarity with Python. Below is a more detailed
walkthrough if you're setting up a Python project for the first time.

1. **Install Python 3** – download it from [python.org](https://www.python.org/)
   if it isn't already installed. You can check by running `python3 --version`
   in your terminal.
2. **Create a virtual environment** – this is a folder that keeps the
   dependencies for this project separate from the rest of your system. Run:

   ```bash
   python3 -m venv venv
   ```

   Then activate it:

   ```bash
   source venv/bin/activate  # On Windows use "venv\Scripts\activate"
   ```

   After activation your prompt will show `(venv)` at the beginning.
3. **Install dependencies** – the packages the app needs are listed in
   `requirements.txt` (currently only `Flask`). Install them with:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server** – start the Flask application with:

   ```bash
   python app.py
   ```

   Visit `http://localhost:5000` in your browser. Use tools like `curl` or
   Postman to send requests to the API endpoints described above.
5. **Deactivate the environment** – when you're done, simply run `deactivate`
   to leave the virtual environment.

If you ever remove the `venv/` folder, you can recreate it using the same steps
above. The SQLite database (`app.db`) and uploaded files (`uploads/`) are stored
locally in the project directory.
