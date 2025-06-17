from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import xml.etree.ElementTree as ET
from collections import defaultdict
import statistics
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DB_PATH = 'app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    input_type TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT,
                    metric_date TEXT,
                    value REAL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS habit_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER,
                    entry_date TEXT,
                    value TEXT,
                    FOREIGN KEY(habit_id) REFERENCES habits(id)
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/habits', methods=['POST'])
def create_habit():
    data = request.form if request.form else request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    name = data.get('name')
    input_type = data.get('input_type')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO habits (name, input_type) VALUES (?, ?)', (name, input_type))
    conn.commit()
    habit_id = c.lastrowid
    conn.close()
    if request.form:
        return redirect(url_for('index'))
    return jsonify({'id': habit_id, 'name': name, 'input_type': input_type})

@app.route('/habit_entries', methods=['POST'])
def add_entry():
   data = request.form if request.form else request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    habit_id = data.get('habit_id')
    entry_date = data.get('entry_date')
    value = data.get('value')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO habit_entries (habit_id, entry_date, value) VALUES (?, ?, ?)',
              (habit_id, entry_date, value))
    conn.commit()
    conn.close()
    if request.form:
        return redirect(url_for('index'))
    return jsonify({'status': 'ok'})

@app.route('/upload', methods=['POST'])
def upload_xml():
    if 'file' not in request.files:
        return 'No file', 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    metrics = parse_xml(path)
    if request.form:
        # When called from HTML form, show metrics on the index page
        return render_template('index.html', metrics=list(metrics.keys()))
    return jsonify({'metrics_found': list(metrics.keys())})

def parse_xml(path):
    """Parse XML and store daily aggregates in the DB."""
    daily = defaultdict(lambda: defaultdict(list))
    for event, elem in ET.iterparse(path, events=('end',)):
        if elem.tag == 'Record':
            mtype = elem.attrib.get('type')
            value = elem.attrib.get('value')
            start = elem.attrib.get('startDate', '')[:10]
            try:
                num = float(value)
            except (TypeError, ValueError):
                elem.clear()
                continue
            daily[mtype][start].append(num)
            elem.clear()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    metrics_found = set()
    for mtype, days in daily.items():
        for date, values in days.items():
            if mtype == 'HKQuantityTypeIdentifierStepCount':
                val = sum(values)
            else:
                val = statistics.mean(values)
            c.execute('INSERT INTO daily_metrics (metric_type, metric_date, value) VALUES (?, ?, ?)',
                      (mtype, date, val))
            metrics_found.add(mtype)
    conn.commit()
    conn.close()
    return {m: None for m in metrics_found}

@app.route('/analytics', methods=['GET'])
def analytics():
    """Very simple analytics on stored metrics and habits."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT metric_date, value FROM daily_metrics WHERE metric_type=?", (
        'HKQuantityTypeIdentifierStepCount',))
    steps = {d: v for d, v in c.fetchall()}

    c.execute("SELECT metric_date, value FROM daily_metrics WHERE metric_type=?", (
        'HKQuantityTypeIdentifierHeartRateVariabilitySDNN',))
    hrv = {d: v for d, v in c.fetchall()}

    avg_steps = statistics.mean(steps.values()) if steps else 0
    avg_hrv = statistics.mean(hrv.values()) if hrv else 0

    message_parts = [
        f"Average daily steps: {avg_steps:.0f}",
        f"Average HRV: {avg_hrv:.0f}"
    ]

    common = [d for d in steps if d in hrv]
    if len(common) > 1:
        import numpy as np
        step_vals = [steps[d] for d in common]
        hrv_vals = [hrv[d] for d in common]
        corr = float(np.corrcoef(step_vals, hrv_vals)[0, 1])
        message_parts.append(f"Correlation between steps and HRV: {corr:.2f}")

    # Simple habit effect on HRV for boolean habits
    c.execute("SELECT id, name FROM habits WHERE input_type='boolean'")
    habits = c.fetchall()
    for hid, name in habits:
        c.execute("SELECT entry_date, value FROM habit_entries WHERE habit_id=?", (hid,))
        entries = {d: v for d, v in c.fetchall()}
        yes_vals = [hrv[d] for d, v in entries.items() if v.lower() in ('1', 'yes', 'true') and d in hrv]
        no_vals = [hrv[d] for d, v in entries.items() if v.lower() in ('0', 'no', 'false') and d in hrv]
        if yes_vals and no_vals:
            diff = statistics.mean(yes_vals) - statistics.mean(no_vals)
            message_parts.append(
                f"When '{name}' is yes, HRV changes by {diff:+.1f} ms")

    conn.close()
    message = '. '.join(message_parts)
    if request.args.get('json') == '1':
        return jsonify({'message': message})
    return render_template('analytics.html', message=message)

@app.route('/')
def index():
    """Render a simple page with forms for common actions."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
