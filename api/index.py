from flask import Flask, request, jsonify
from google import genai
import sqlite3
from dotenv import load_dotenv
import os
import resend
import random
sqliteurl = "users.db"
import numpy as np
import resemblyzer
from fastapi import FastAPI, File
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
client = genai.Client()

def init_db():
    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            voicedata BLOB
        )
    """)
    conn.commit()
    conn.close()

init_db()

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

    
# Creates a user with all of the data
@app.route("/api/create_user", methods=["POST"])
def create_user():
    username = request.form.get("username")
    password = request.form.get("password")
    voice_file = request.files.get("voicedata")
    
    if not username or not password or not voice_file:
        return jsonify({"error": "Username, password, and voice file are required"}), 400
    
    # Read the file content as bytes
    voicedata = voice_file.read()
    
    try:
        conn = sqlite3.connect(sqliteurl)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, voicedata) VALUES (?, ?, ?)",
            (username, password, voicedata)
        )
        conn.commit()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already taken"}), 409
    finally:
        conn.close()



@app.route("/api/get_voicedata/<username>", methods=["GET"])
def get_voicedata(username):
    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute("SELECT voicedata FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return row[0], 200, {'Content-Type': 'audio/wav'}
    else:
        return jsonify({"error": "User not found or no voice data"}), 404



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

    if len(password < 10):
        return jsonify({"error": "Password must be 10 characters or longer"}), 400

    contains_special = False
    contains_capital = False
    for c in password:
        # if a character is not a letter or a number
        if not c.isalnum():
            contains_special = True
        # if a character is upper case
        elif c.isupper():
            contains_capital = True

    if (not contains_capital) or (not contains_special):
        return jsonify({"error": "Password must contain atleast one capital letter and one special character"}), 400
    
    conn = sqlite3.connect(sqliteurl)
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

    
resend.api_key = os.getenv("RESEND_API_KEY")
@app.route("/api/send_verification", methods=["POST"])
def send_verification():
    data = request.get_json()
    email = data.get("email")
    code = str(random.randint(100000, 999999))

    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_codes (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL
        )
    """)
    cursor.execute(
        "INSERT OR REPLACE INTO verification_codes (email, code) VALUES (?, ?)",
        (email, code)
    )
    conn.commit()
    conn.close()

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Your Verification Code",
        "html": f"<p>Your verification code is: <strong>{code}</strong></p>"
    })

    return jsonify({"message": "Code sent"}), 200

@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT code FROM verification_codes WHERE email = ?", (email,)
    )
    row = cursor.fetchone()
    print("DB row:", row)        # add this
    print("Code entered:", code) # add this
    if row and row[0] == code:
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Verified!"}), 200
    conn.close()
    return jsonify({"error": "Invalid code"}), 401



fastapi_app = FastAPI()
encoder = VoiceEncoder()

def compare_voices(file1, file2, threshold=0.75):
    emb1 = encoder.embed_utterance(preprocess_wav(Path(file1)))
    emb2 = encoder.embed_utterance(preprocess_wav(Path(file2)))
    
    similarity = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    return {
        "similarity": round(similarity, 3),
        "match": similarity >= threshold
    }

def save_blob_to_wav(blob_data: bytes, filename: str):
    """Save BLOB data to a .wav file."""
    with open(filename, "wb") as f:
        f.write(blob_data)

@fastapi_app.route("/api/compare_voices", methods=["POST"])
async def compare_voices_endpoint(
    enrolled: bytes = File(...),
    verify: bytes = File(...)
):
    # Save BLOB data to temporary .wav files
    save_blob_to_wav(enrolled, "enrolled.wav")
    save_blob_to_wav(verify, "verify.wav")

    result = compare_voices("enrolled.wav", "verify.wav")

    os.remove("enrolled.wav")
    os.remove("verify.wav")

    return result



if __name__ == "__main__":
    app.run(port=5328)