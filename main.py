
from flask import Flask, render_template, request, jsonify, session
import ollama
import os

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)

MODEL = "qwen3:8b"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/new-chat", methods=["POST"])
def new_chat():
    session.pop("history", None)
    return jsonify({"message": "New chat started."})



@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("message", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    history = session.get("history", [])
    history.append({"role": "user", "content": question})

    try:
        response = ollama.chat(
            model=MODEL,
            messages=history
        )

        answer = response["message"]["content"]
        history.append({"role": "assistant", "content": answer})

        # Keep the most recent messages to limit memory usage.
        session["history"] = history[-10:]

        return jsonify({"reply": answer})

    except Exception:
        app.logger.exception("Ollama request failed")
        return jsonify({
            "error": "Could not get a response from Ollama."
        }), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=False)
