from flask import Blueprint, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .scheme_loader import load_schemes, search_relevant_schemes, build_context_from_results

chatbot = Blueprint('chatbot', __name__)

# Load environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("⚠️ GEMINI_API_KEY not found")
    model = None
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-flash-latest")

# Load full dataset once
df = load_schemes()

PROJECT_CONTEXT = """
You are GovSahayak AI, an intelligent assistant for the PrajaGuide platform.

About the platform:
- It analyzes 3400+ government schemes.
- Uses AI + rule engine to match users with schemes.
- Helps citizens discover, understand, and apply for benefits.
- Supports central and state schemes.

Your role:
- Answer questions about schemes.
- Explain eligibility simply.
- Guide users step by step.
- Explain how the platform works.
- Be clear, friendly, and concise.
"""

@chatbot.route("/chat", methods=["POST"])
def chat():
    try:
        if not model:
            return jsonify({"reply": "Chatbot not configured."})

        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please type a question."})

        # Retrieve relevant schemes
        relevant = search_relevant_schemes(df, user_message, top_k=5)
        scheme_context = build_context_from_results(relevant)

        # Build final prompt
        prompt = (
            PROJECT_CONTEXT +
            "\nRelevant schemes:\n" +
            scheme_context +
            f"\nUser: {user_message}\nAssistant:"
        )

        response = model.generate_content(prompt)

        return jsonify({"reply": response.text})

    except Exception as e:
        print("Chatbot error:", e)
        return jsonify({"reply": "Assistant temporarily unavailable."})
