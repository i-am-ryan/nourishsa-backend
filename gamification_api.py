from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

DB_FILE = "gamification.db"

# 🛠️ Initialize the DB if it doesn't exist
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                kg REAL,
                date TEXT
            )
        """)

app = Flask(__name__)
CORS(app)

# 🚀 Endpoint to submit a donation
@app.route("/api/submit-donation", methods=["POST"])
def submit_donation():
    data = request.get_json()
    username = data.get("username")
    kg = float(data.get("kg", 0))
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO donations (username, kg, date) VALUES (?, ?, ?)",
            (username, kg, date)
        )

    return jsonify({"success": True})


# 📊 Endpoint to fetch gamification stats
@app.route("/api/gamification-stats", methods=["POST"])
def gamification_stats():
    data = request.get_json()
    username = data.get("username")

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT kg, date FROM donations WHERE username = ?", (username,))
        rows = cur.fetchall()

    total_kg = sum(row[0] for row in rows)
    xp = int(total_kg * 10)

    # 🧠 Calculate daily streak
    dates = sorted(set(row[1] for row in rows))
    streak = 0
    today = datetime.now().date()

    for i in range(len(dates)-1, -1, -1):
        donation_date = datetime.strptime(dates[i], "%Y-%m-%d").date()
        if (today - donation_date).days == streak:
            streak += 1
        else:
            break

    # 🏆 Determine badges
    badges = []
    if total_kg >= 60:
        badges.append("🥉 Bronze Saver")
    if total_kg >= 100:
        badges.append("🥈 Silver Saver")
    if total_kg >= 200:
        badges.append("🥇 Gold Saver")
    if streak >= 3:
        badges.append("🔥 3-Day Streak")
    if streak >= 7:
        badges.append("🔥🔥 7-Day Streak")

    return jsonify({
        "success": True,
        "stats": {
            "totalKg": total_kg,
            "xp": xp,
            "streak": streak,
            "lastDonationDate": dates[-1] if dates else None,
            "badges": badges
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
