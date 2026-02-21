from flask import Flask
app = Flask(__name__)

@app.route("/api/gemini")
def text_auth():
    return "<p>Hello, World!</p>"