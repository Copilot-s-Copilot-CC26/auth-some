from flask import Flask, request, jsonify
from google import genai
import sqlite3
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
client = genai.Client()

@app.route("/api/gemini", methods=["POST"])
def gemini_prompt():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    prompt = data.get("prompt")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return jsonify({"result": response.text}), 200

    
@app.route("/api/create_user", methods=["POST"])
def create_user():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get("username")
    password = data.get("password")
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already taken"}), 409
    finally:
        conn.close()



# gets a user and password combination from the frontend and compares
# it with each database entry. If it matches one, returns
@app.route("/api/validate_user", methods=["POST"])
def validate_user():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    # gets the username and password from data and stores them
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    conn.commit()

    # Query users
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    for row in rows:
        if row[1] == username and row[2] == password:
            conn.close()
            # found a matching user
            return jsonify({"message": "Login successful"}), 200
    conn.close()
    return jsonify({"error": "Incorrect login information!"}), 400

if __name__ == "__main__":
    app.run(port=5328)
    
    



   