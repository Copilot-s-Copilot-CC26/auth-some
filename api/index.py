from flask import Flask, request, jsonify
from google import genai
import sqlite3
from dotenv import load_dotenv
import os
import resend
import random
from twilio.rest import Client
sqliteurl = "users.db"
# import numpy as np


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
        conn = sqlite3.connect(sqliteurl)
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
        "from": "onboarding@auth-some.andysorge.xyz",
        "to": email,
        "subject": "Your Verification Code",
        "html": f"<p>Your verification code is: <strong>{code}</strong></p>"
    })

    return jsonify({"message": "Code sent"}), 200

@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = int(data.get("code"))
    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT code FROM verification_codes WHERE email = ?", (email,)
    )
    row = cursor.fetchone()
    if row and int( row[0]) == code:
        cursor.execute("DELETE FROM verification_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Verified!"}), 200
    conn.close()
    return jsonify({"error": "Invalid code"}), 401



# app = FastAPI()
# encoder = VoiceEncoder()

# def compare_voices(file1, file2, threshold=0.75):
#     emb1 = encoder.embed_utterance(preprocess_wav(Path(file1)))
#     emb2 = encoder.embed_utterance(preprocess_wav(Path(file2)))
    
#     similarity = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
#     return {
#         "similarity": round(similarity, 3),
#         "match": similarity >= threshold
#     }

# @app.route("/api/compare_voices", methods=["POST"])
# async def compare_voices_endpoint(
#     enrolled: UploadFile = File(...),
#     verify: UploadFile = File(...)
# ):
#     for upload, name in [(enrolled, "enrolled.wav"), (verify, "verify.wav")]:
#         with open(name, "wb") as f:
#             shutil.copyfileobj(upload.file, f)

#     result = compare_voices("enrolled.wav", "verify.wav")

#     os.remove("enrolled.wav")
#     os.remove("verify.wav")

    return result



if __name__ == "__main__":
    app.run(port=5328)

twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

@app.route("/api/send_text_verification", methods=["POST"])
def send_text_verification():
    data = request.get_json()
    phone = data.get("phone")
    
    verification = twilio_client.verify.v2.services(os.getenv("TWILIO_VERIFY_SID")).verifications.create(
        to=phone,
        channel="sms"
    )
    
    return jsonify({"message": "Code sent"}), 200

@app.route("/api/verify_text_code", methods=["POST"])
def verify_text_code():
    data = request.get_json()
    phone = data.get("phone")
    code = data.get("code")
    
    result = twilio_client.verify.v2.services(os.getenv("TWILIO_VERIFY_SID")).verification_checks.create(
        to=phone,
        code=code
    )
    
    if result.status == "approved":
        return jsonify({"message": "Verified!"}), 200
    return jsonify({"error": "Invalid code"}), 401

