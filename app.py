from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route("/api/skill-tutorial", methods=["POST"])
def skill_tutorial():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query required"}), 400

    prompt = f"""You're an expert in food preservation and community gardening. 
Respond with a practical and localized tutorial (with steps or a checklist) for: "{query}".
Make sure it's beginner-friendly and applicable in South African townships."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = response.choices[0].message["content"]
        return jsonify({"tutorial": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Health check
@app.route("/")
def home():
    return "✅ NourishSA backend is live!"

# Route 1: Smart Bundle Builder
@app.route("/api/generate-bundle", methods=["POST"])
def generate_bundle():
    data = request.get_json()
    preference = data.get("preference", "budget")

    prompt = f"Suggest a 3-item food bundle for a {preference} diet using common surplus food in South Africa."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        message = response.choices[0].message.content
        items = [item.strip("•- \n") for item in message.split("\n") if item.strip()]
        return jsonify({"bundle": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route 2: Budget Meal Generator (e.g., R50 meals)
@app.route("/api/meal-by-budget", methods=["POST"])
def generate_meal_by_budget():
    data = request.get_json()
    budget = data.get("budget", 50)

    prompt = (
        f"You're an AI helping low-income South Africans eat healthy. Suggest a filling, nutritious meal "
        f"that costs no more than R{budget}. Include a meal name, ingredients, cooking steps, and estimated cost."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"success": True, "meal": reply})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
    # Route 3: AI-Powered Skill Trainer
@app.route("/api/skill-trainer", methods=["POST"])
def skill_trainer():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"success": False, "error": "No question provided"}), 400

    prompt = (
        f"You are a helpful South African food and agriculture training assistant. "
        f"Provide a clear, friendly step-by-step guide for this query:\n\n"
        f"'{query}'\n\n"
        f"Include a checklist if applicable and practical tips using local township methods."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT username, SUM(kg) as totalKg
            FROM donations
            GROUP BY username
            ORDER BY totalKg DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
    return jsonify([{"username": row[0], "totalKg": row[1], "xp": int(row[1]*10)} for row in rows])


# Run server
if __name__ == "__main__":
    app.run(debug=True)
