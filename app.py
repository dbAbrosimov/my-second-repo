from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import xml.etree.ElementTree as ET
from collections import defaultdict
import statistics
import pandas as pd
import numpy as np
import os
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DB_PATH = 'app.db'

# Configurable start of day as HH:MM (default 03:00)
DAY_START_HOUR = os.environ.get('DAY_START_HOUR', '03:00')
try:
    _h, _m = map(int, DAY_START_HOUR.split(':'))
    DAY_START_TIME = datetime.time(_h, _m)
except Exception:
    DAY_START_TIME = datetime.time(3, 0)

TRIVIAL_PAIRS = {frozenset({'Body Fat Percentage', 'Body Mass'})}

def prettify_type(raw):
    """Convert HK type names to a readable form."""
    if not raw:
        return raw
    prefixes = [
        'HKQuantityTypeIdentifier',
        'HKCategoryTypeIdentifier',
        'HKCorrelationTypeIdentifier',
    ]
    for p in prefixes:
        if raw.startswith(p):
            raw = raw[len(p):]
            break
    if raw.startswith('Apple'):
        raw = raw[len('Apple'):]
    if raw.startswith('Sleeping'):
        raw = raw[len('Sleeping'):]
    if raw.startswith('HK'):
        raw = raw[2:]
    if raw.endswith('Identifier'):
        raw = raw[:-10]
    words = []
    buf = raw[0]
    for ch in raw[1:]:
        if ch.isupper() and buf[-1].islower():
            words.append(buf)
            buf = ch
        else:
            buf += ch
    words.append(buf)
    name = ' '.join(w.capitalize() for w in words)
    return name

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
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

init_db()

@app.route('/habits', methods=['POST'])
def create_habit():
    data = request.form if request.form else request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    name = data.get('name')
    input_type = data.get('input_type')
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO habits (name, input_type) VALUES (?, ?)', (name, input_type))
        habit_id = c.lastrowid
    if request.form:
        return redirect(url_for('index'))
    return jsonify({'id': habit_id, 'name': name, 'input_type': input_type})

@app.route('/habit_entries', methods=['POST'])
def add_entry():
    """Store a single habit entry for the given date."""
    data = request.form if request.form else request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    habit_id = data.get('habit_id')
    entry_date = data.get('entry_date')
    value = data.get('value')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            'INSERT INTO habit_entries (habit_id, entry_date, value) '
            'VALUES (?, ?, ?)',
            (habit_id, entry_date, value)
        )

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
            raw_type = elem.attrib.get('type')
            value = elem.attrib.get('value')
            start_date = elem.attrib.get('startDate')
            end_date = elem.attrib.get('endDate')
            mtype = prettify_type(raw_type)

            day_key = None
            s_dt = e_dt = None
            if start_date:
                try:
                    s_dt = datetime.datetime.fromisoformat(start_date)
                    e_dt = datetime.datetime.fromisoformat(end_date) if end_date else None
                    day_key = s_dt.date().isoformat()
                    cutoff = datetime.datetime.combine(s_dt.date(), DAY_START_TIME)
                    if e_dt and s_dt.time() < DAY_START_TIME and e_dt > cutoff:
                        day_key = (s_dt.date() + datetime.timedelta(days=1)).isoformat()
                except Exception:
                    day_key = start_date[:10]

            try:
                num = float(value)
            except (TypeError, ValueError):
                if raw_type and raw_type.endswith('SleepAnalysis') and s_dt and e_dt:
                    try:
                        num = (e_dt - s_dt).total_seconds() / 60
                        stage = prettify_type(value)
                        stage = stage.replace('Category Value Sleep Analysis ', '')
                        mtype = stage
                    except Exception:
                        elem.clear()
                        continue
                else:
                    elem.clear()
                    continue

            if day_key:
                daily[mtype][day_key].append(num)
            elem.clear()

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        metrics_found = set()
        for mtype, days in daily.items():
            for date, values in days.items():
                if mtype == 'Step Count' or 'Asleep' in mtype or 'Awake' in mtype or 'Bed' in mtype:
                    val = sum(values)
                else:
                    val = statistics.mean(values)
                c.execute('INSERT INTO daily_metrics (metric_type, metric_date, value) VALUES (?, ?, ?)',
                          (mtype, date, val))
                metrics_found.add(mtype)
    return {m: None for m in metrics_found}

@app.route('/analytics', methods=['GET'])
def analytics():
    """Compute correlations between metrics and habits."""
    accuracy = request.args.get('accuracy', 'medium')
    thresholds = {'high': 0.6, 'medium': 0.4, 'low': 0.2}
    min_points = {'high': 30, 'medium': 15, 'low': 5}
    thresh = thresholds.get(accuracy, 0.4)
    min_pts = min_points.get(accuracy, 15)
    show_trivial = request.args.get('show_trivial') == '1'

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query('SELECT metric_date, metric_type, value FROM daily_metrics', conn)
        habits_df = pd.read_sql_query(
            'SELECT habit_entries.entry_date, habits.name, habits.input_type, habit_entries.value '
            'FROM habit_entries JOIN habits ON habit_entries.habit_id = habits.id',
            conn
        )

    if df.empty:
        return render_template('analytics.html', message='No metrics uploaded yet')

    pivot = df.pivot_table(values='value', index='metric_date', columns='metric_type', aggfunc='first')

    if not habits_df.empty:
        def conv(row):
            t = row['input_type']
            val = row['value']
            if t == 'boolean':
                return 1 if str(val).lower() in ('1', 'yes', 'true', 'да') else 0
            if t == 'scale3':
                mapping = {'low': 1, 'medium': 2, 'high': 3}
                return mapping.get(str(val).lower())
            if t == 'scale5':
                try:
                    n = int(val)
                    if 1 <= n <= 5:
                        return float(n)
                except ValueError:
                    return None
            try:
                return float(val)
            except ValueError:
                return None

        habits_df['num_val'] = habits_df.apply(conv, axis=1)
        habit_pivot = habits_df.pivot_table(values='num_val', index='entry_date', columns='name', aggfunc='first')
        pivot = pivot.join(habit_pivot, how='left')

    corr_matrix = pivot.corr(min_periods=min_pts)
    pairs_df = (
        corr_matrix
        .where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        .stack()
        .rename_axis(index=("metric1", "metric2"))
        .reset_index(name="corr")
    )

    if not show_trivial:
        mask = pairs_df.apply(
            lambda r: frozenset({r['metric1'], r['metric2']}) in TRIVIAL_PAIRS,
            axis=1,
        )
        pairs_df = pairs_df[~mask]

    pairs_df = pairs_df[(pairs_df['corr'].abs() >= thresh) & (pairs_df['corr'].abs() < 0.99)]

    correlations = []
    summaries = []
    for _, row in pairs_df.iterrows():
        c1, c2, corr = row['metric1'], row['metric2'], row['corr']
        correlations.append((c1, c2, corr))
        sub = pivot[[c1, c2]].dropna()
        if len(sub) >= 2:
            slope, _ = np.polyfit(sub[c1], sub[c2], 1)
            mean_x = sub[c1].mean()
            mean_y = sub[c2].mean()
            step = sub[c1].std()
            if step:
                predicted = mean_y + slope * step
                summaries.append(
                    f"If your {c1.lower()} rises from {mean_x:.0f} to {mean_x+step:.0f}, "
                    f"{c2.lower()} may change from {mean_y:.0f} to {predicted:.0f}."
                )

    lines = [f"Accuracy: {accuracy}", f"Found {len(correlations)} significant correlations"]
    for c1, c2, corr in correlations:
        lines.append(f"{c1} vs {c2}: {corr:+.2f}")

    message = '\n'.join(lines)
    if request.args.get('json') == '1':
        return jsonify({'correlations': correlations, 'summaries': summaries})
    return render_template('analytics.html', message=message, summaries=summaries, accuracy=accuracy)

@app.route('/')
def index():
    """Render a simple page with forms for common actions."""
    with sqlite3.connect(DB_PATH) as conn:
        habits = conn.execute('SELECT id, name, input_type FROM habits').fetchall()
        today = datetime.date.today().strftime('%Y-%m-%d')
        return render_template('index.html', habits=habits, today=today)

if __name__ == '__main__':
    app.run(debug=True)
