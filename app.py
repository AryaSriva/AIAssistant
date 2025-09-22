from flask import Flask, render_template, request, jsonify, session
import openai
import os
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Load environment variables
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

# Initialize OpenAI client
client = openai.OpenAI(
    base_url=endpoint,
    api_key=token,
)


def load_context():
    """Load conversation context from file"""
    try:
        with open("context.txt", "r") as file:
            messages = []
            for line in file:
                if line.strip():
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        role = parts[0]
                        content = parts[1].strip()
                        messages.append({"role": role, "content": content})
            return (
                messages
                if messages
                else [{"role": "system", "content": "You are a helpful assistant."}]
            )
    except FileNotFoundError:
        return [{"role": "system", "content": "You are a helpful assistant."}]


def save_context(messages):
    """Save conversation context to file"""
    with open("context.txt", "w") as file:
        for message in messages:
            file.write(f"{message['role']}:{message['content']}\n")


@app.route("/")
def index():
    """Render the main chat interface"""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Get or create session messages
        if "messages" not in session:
            session["messages"] = load_context()

        messages = session["messages"]

        # Add user message
        messages.append({"role": "user", "content": user_message})

        # Get AI response
        response = client.chat.completions.create(
            messages=messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name,
        )

        assistant_message = response.choices[0].message.content

        # Add assistant response
        messages.append({"role": "assistant", "content": assistant_message})

        # Update session
        session["messages"] = messages
        session.modified = True

        # Save to file
        save_context(messages)

        return jsonify({"response": assistant_message, "success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    """Clear the conversation history"""
    try:
        session["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        session.modified = True
        save_context(session["messages"])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    """Get conversation history"""
    try:
        if "messages" not in session:
            session["messages"] = load_context()

        # Filter out system messages for display
        display_messages = [
            msg for msg in session["messages"] if msg["role"] != "system"
        ]

        return jsonify({"messages": display_messages, "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
