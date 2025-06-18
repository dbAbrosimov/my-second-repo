# Health Habit Tracker (Prototype)

This is a minimal Flask application demonstrating how one might upload Apple Health XML data,
create daily habits, store entries, and explore correlations between them.
For Mac users, see **README_mac_ru.md** for a simplified guide in Russian.

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

The server listens on `http://localhost:5000`. Opening this URL in a browser
shows a simple page styled with **Bootstrap**. You can upload an XML file and
create habits there. Existing habits are listed with buttons so you can quickly
mark today&#39;s values.
After uploading a file, the page lists the metrics it detected.
Uploaded data are aggregated per day and stored in a small SQLite database.
The `/analytics` page now computes correlations between all stored metrics and
habit entries. Metric names are shown in a human friendly form (e.g. `Apple Stand Time`).
Use the query parameter `accuracy` (`high`, `medium`, or `low`) or the buttons on the analytics page
to control how strict the correlation threshold is. Trivial relations like
`Body Fat Percentage` vs `Body Mass` are hidden unless `show_trivial=1` is passed.

## Endpoints

- `POST /upload` – upload an Apple Health XML file (can be called from the web form or via `curl`).
- `POST /habits` – create a habit. Accepts JSON or form data with `name` and `input_type`.
- `POST /habit_entries` – add an entry. Accepts JSON or form data with `habit_id`, `entry_date` (YYYY-MM-DD), and `value`.
- `GET /analytics` – show basic statistics and correlations.
- `GET /` – renders a simple HTML page with forms.

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
   `requirements.txt` (`Flask`, `numpy`, and `pandas`). Install them with:

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
# Health Habit Tracker (Prototype)

This is a minimal Flask application demonstrating how one might upload Apple Health XML data,
create daily habits, store entries, and explore correlations between them.
For Mac users, see **README_mac_ru.md** for a simplified guide in Russian.

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

The server listens on `http://localhost:5000`. Opening this URL in a browser
shows a simple page with forms for uploading an XML file and creating habits.
Existing habits are listed with buttons so you can quickly mark today&#39;s values.
After uploading a file, the page lists the metrics it detected.
Uploaded data are aggregated per day and stored in a small SQLite database.
The `/analytics` page now computes correlations between all stored metrics and
habit entries. Metric names are shown in a human friendly form (e.g. `Apple Stand Time`).
Use the query parameter `accuracy` (`high`, `medium`, or `low`) or the buttons on the analytics page
to control how strict the correlation threshold is. Trivial relations like
`Body Fat Percentage` vs `Body Mass` are hidden unless `show_trivial=1` is passed.

## Endpoints

- `POST /upload` – upload an Apple Health XML file (can be called from the web form or via `curl`).
- `POST /habits` – create a habit. Accepts JSON or form data with `name` and `input_type`.
- `POST /habit_entries` – add an entry. Accepts JSON or form data with `habit_id`, `entry_date` (YYYY-MM-DD), and `value`.
- `GET /analytics` – show basic statistics and correlations.
- `GET /` – renders a simple HTML page with forms.

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
   `requirements.txt` (`Flask`, `numpy`, and `pandas`). Install them with:

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
# Health Habit Tracker (Prototype)

This is a minimal Flask application demonstrating how one might upload Apple Health XML data,

For Mac users, see **README_mac_ru.md** for a simplified guide in Russian.

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


The server listens on `http://localhost:5000`. Opening this URL in a browser
shows a simple page with forms for uploading an XML file and creating habit
entries. After uploading a file, the page lists the metrics it detected.
Uploaded data are aggregated per day and stored in a small SQLite database.

The `/analytics` page now computes correlations between all stored metrics and
habit entries. Use the query parameter `accuracy` (`high`, `medium`, or `low`)
to control how strict the correlation threshold is.


## Endpoints

- `POST /upload` – upload an Apple Health XML file (can be called from the web form or via `curl`).
- `POST /habits` – create a habit. Accepts JSON or form data with `name` and `input_type`.
- `POST /habit_entries` – add an entry. Accepts JSON or form data with `habit_id`, `entry_date` (YYYY-MM-DD), and `value`.
- `GET /analytics` – show basic statistics and correlations.
- `GET /` – renders a simple HTML page with forms.

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
   `requirements.txt` (`Flask`, `numpy`, and `pandas`). Install them with:

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
