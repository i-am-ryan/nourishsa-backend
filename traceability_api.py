from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Database setup
DB_FILE = "traceability.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS trace_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor TEXT NOT NULL,
                recipient TEXT NOT NULL,
                items TEXT NOT NULL,
                date TEXT NOT NULL,
                qr_code TEXT
            )
        ''')
        conn.commit()

init_db()

# Add a new trace record
@app.route("/api/add-trace", methods=["POST"])
def add_trace():
    data = request.json
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO trace_records (donor, recipient, items, date, qr_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get("donor"),
                data.get("recipient"),
                data.get("items"),
                data.get("date"),
                data.get("qr_code")
            ))
            conn.commit()
        return jsonify(success=True, message="Record added successfully")
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

# Fetch all trace records
@app.route("/api/trace-records", methods=["GET"])
def get_traces():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM trace_records ORDER BY id DESC")
            records = [dict(row) for row in c.fetchall()]
        return jsonify(success=True, records=records)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
