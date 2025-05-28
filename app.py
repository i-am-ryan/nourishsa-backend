from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

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

# Run server
if __name__ == "__main__":
    app.run(debug=True)
