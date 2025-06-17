from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import xml.etree.ElementTree as ET
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
    data = request.json
    name = data.get('name')
    input_type = data.get('input_type')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO habits (name, input_type) VALUES (?, ?)', (name, input_type))
    conn.commit()
    habit_id = c.lastrowid
    conn.close()
    return jsonify({'id': habit_id, 'name': name, 'input_type': input_type})

@app.route('/habit_entries', methods=['POST'])
def add_entry():
    data = request.json
    habit_id = data.get('habit_id')
    entry_date = data.get('entry_date')
    value = data.get('value')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO habit_entries (habit_id, entry_date, value) VALUES (?, ?, ?)',
              (habit_id, entry_date, value))
    conn.commit()
    conn.close()
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
    return jsonify({'metrics_found': list(metrics.keys())})

def parse_xml(path):
    metrics = {}
    for event, elem in ET.iterparse(path, events=('end',)):
        if elem.tag == 'Record':
            mtype = elem.attrib.get('type')
            value = elem.attrib.get('value')
            metrics.setdefault(mtype, []).append(value)
            elem.clear()
    return metrics

@app.route('/analytics', methods=['GET'])
def analytics():
    # Placeholder analytics implementation
    return jsonify({'message': 'Analytics not implemented. This is a stub.'})

if __name__ == '__main__':
    app.run(debug=True)
