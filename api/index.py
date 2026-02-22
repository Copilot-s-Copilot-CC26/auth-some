from flask import Flask, request, jsonify
from google import genai
import sqlite3
from dotenv import load_dotenv
import os
import resend
import random
from vonage import Auth, Vonage, HttpClientOptions
from vonage_verify import VerifyRequest, SmsChannel
from vonage_sms import SmsMessage, SmsResponse
import json
sqliteurl = "users.db"
# import numpy as np


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
client = genai.Client()

vonageAuth = Auth(api_key="31a5f7e0", api_secret=os.getenv("VONAGE_API_SECRET"))
vonage = Vonage(auth=vonageAuth)

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
    image_file = request.files.get("image")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    # Read the file content as bytes
    voicedata = voice_file.read() if voice_file else None
    imagedata = image_file.read() if image_file else None
    
    try:
        conn = sqlite3.connect(sqliteurl)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, voicedata, image) VALUES (?, ?, ?, ?)",
            (username, password, voicedata, imagedata)
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



@app.route("/api/get_imagedata/<username>", methods=["GET"])
def get_imagedata(username):
    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return row[0], 200, {'Content-Type': 'image/jpeg'}
    else:
        return jsonify({"error": "User not found or no image data"}), 404



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



# fastapi_app = FastAPI()
# encoder = VoiceEncoder()

# def compare_voices(file1, file2, threshold=0.75):
#     emb1 = encoder.embed_utterance(preprocess_wav(Path(file1)))
#     emb2 = encoder.embed_utterance(preprocess_wav(Path(file2)))
    
#     similarity = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
#     return {
#         "similarity": round(similarity, 3),
#         "match": similarity >= threshold
#     }

# def save_blob_to_wav(blob_data: bytes, filename: str):
#     """Save BLOB data to a .wav file."""
#     with open(filename, "wb") as f:
#         f.write(blob_data)

# def compare_faces(image1_bytes, image2_bytes):
#     try:
#         # Load images from bytes
#         img1 = Image.open(BytesIO(image1_bytes))
#         img2 = Image.open(BytesIO(image2_bytes))
        
#         # Convert to RGB if needed
#         img1 = img1.convert('RGB')
#         img2 = img2.convert('RGB')
        
#         # Get face encodings
#         enc1 = face_recognition.face_encodings(np.array(img1))
#         enc2 = face_recognition.face_encodings(np.array(img2))
        
#         if not enc1:
#             return {"error": "No face found in first image"}
#         if not enc2:
#             return {"error": "No face found in second image"}
        
#         # Compare faces
#         results = face_recognition.compare_faces([enc1[0]], enc2[0])
#         distance = face_recognition.face_distance([enc1[0]], enc2[0])[0]
        
#         return {
#             "match": bool(results[0]),
#             "distance": float(distance)
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @fastapi_app.route("/api/compare_voices", methods=["POST"])
# async def compare_voices_endpoint(
#     enrolled: bytes = File(...),
#     verify: bytes = File(...)
# ):
#     # Save BLOB data to temporary .wav files
#     save_blob_to_wav(enrolled, "enrolled.wav")
#     save_blob_to_wav(verify, "verify.wav")

#     result = compare_voices("enrolled.wav", "verify.wav")

#     os.remove("enrolled.wav")
#     os.remove("verify.wav")

#     return result

@app.route("/api/send_text_verification", methods=["POST"])
def send_text_verification():
    data = request.get_json()
    phone = data.get("phone")
    code = str(random.randint(100000, 999999))

    sms_channel = SmsChannel(to=str(phone), from_="19896137088")
    params = {
        'brand': 'Vonage',
        'workflow': [sms_channel],
    }
    verify_request = VerifyRequest(**params)

    response = vonage.verify.start_verification(verify_request)

    responseDict = json.loads(response.model_dump_json())

    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS text_verification_codes (
            phone TEXT PRIMARY KEY,
            request_id TEXT NOT NULL
        )
    """)
    cursor.execute(
        "INSERT OR REPLACE INTO text_verification_codes (phone, request_id) VALUES (?, ?)",
        (phone, responseDict["request_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Code sent"}), 200

@app.route("/api/verify_text_code", methods=["POST"])
def verify_text_code():
    data = request.get_json()
    phone = data.get("phone")
    code = data.get("code")
    conn = sqlite3.connect(sqliteurl)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT request_id FROM text_verification_codes WHERE phone = ?", (phone,)
    )
    row = cursor.fetchone()

    if row:
        response = vonage.verify.check_code(request_id=row[0], code=code)
        if json.loads(response.model_dump_json())["status"] == 'completed':
            cursor.execute("DELETE FROM text_verification_codes WHERE phone = ?", (phone,))
            conn.commit()
            conn.close()
            return jsonify({"message": "Verified!"}), 200
    conn.close()
    return jsonify({"error": "Invalid code"}), 401

