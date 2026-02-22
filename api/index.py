from flask import Flask, request, jsonify
import sqlite3
from dotenv import load_dotenv
import os
import resend
import random
from vonage import Auth, Vonage
from vonage_verify import VerifyRequest, SmsChannel
import json

from api.utils import bytes_to_image
from utils import setup_database, compare_faces, compare_voices

# BEGIN SETUP
load_dotenv()
# END SETUP

# DATABASE CONFIG
DB_URL = os.getenv("DATABASE_URL")
setup_database(DB_URL)
# END DATABASE CONFIG

# client = genai.Client()

# VONAGE CONFIG
vonageAuth = Auth(api_key=os.getenv("VONAGE_API_KEY"), api_secret=os.getenv("VONAGE_API_SECRET"))
vonage = Vonage(auth=vonageAuth)
# END VONAGE CONFIG

# INIT FLASK
app = Flask(__name__)
#END INIT FLASK

#-----------------------------USER MANAGEMENT-----------------------------

# creates new user and inserts into users and user_data
@app.route("/api/create_user", methods=["POST"])
def create_user():
    conn = sqlite3.connect(DB_URL)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # Insert into users table
        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (?, ?)
            """,
            (request.form.get("username"), request.form.get("password"))
        )

        user_id = cursor.lastrowid

        voice = request.files.get("voice")
        image = request.files.get("image")

        image_bytes = image.read() if image else None
        voice_bytes = voice.read() if voice else None

        # Insert into user_data table
        cursor.execute(
            """
            INSERT INTO user_data (
                user_id,
                first_name,
                middle_name,
                last_name,
                suffix,
                phone,
                address_line_1,
                address_line_2,
                city,
                state,
                zip_code,
                sleep_coords,
                credit_card_number,
                expiration_month,
                expiration_year,
                cvc,
                social_security_number,
                license_plate,
                license_plate_state,
                date_of_birth,
                mothers_maiden_name,
                voice,
                face
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                request.form.get("first-name"),
                request.form.get("middle-name"),
                request.form.get("last-name"),
                request.form.get("suffix"),
                request.form.get("phone"),
                request.form.get("address-line-1"),
                request.form.get("address-line-2"),
                request.form.get("city"),
                request.form.get("state"),
                request.form.get("zip-code"),
                request.form.get("sleep-coords"),
                request.form.get("credit-card-number"),
                request.form.get("expiration-month"),
                request.form.get("expiration-year"),
                request.form.get("cvc"),
                request.form.get("social-security-number"),
                request.form.get("license-plate"),
                request.form.get("license-plate-state"),
                request.form.get("date-of-birth"),
                request.form.get("mother's-maiden-name"),
                voice_bytes,
                image_bytes
            )
        )

        conn.commit()
        return jsonify({"message": "User created", "user_id": user_id}), 201

    except sqlite3.IntegrityError as e:
        app.logger.error(e)
        conn.rollback()
        return jsonify({"error": "Username already exists"}), 400

    finally:
        conn.close()

# checks if a username and password are correct
@app.route("/api/validate_user", methods=["POST"])
def validate_user():
    username = request.form.get("username")
    password = request.form.get("password")

    new_face = request.files.get("image")
    new_voice = request.files.get("voice")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # if len(password < 10):
    #     return jsonify({"error": "Password must be 10 characters or longer"}), 400
    #
    # contains_special = False
    # contains_capital = False
    # for c in password:
    #     # if a character is not a letter or a number
    #     if not c.isalnum():
    #         contains_special = True
    #     # if a character is upper case
    #     elif c.isupper():
    #         contains_capital = True
    #
    # if (not contains_capital) or (not contains_special):
    #     return jsonify({"error": "Password must contain atleast one capital letter and one special character"}), 400

    conn = sqlite3.connect(DB_URL)
    crsr = conn.cursor()

    crsr.execute("""
                 SELECT u.id, ud.face, ud.voice
                 FROM users u
                          JOIN user_data ud ON u.id = ud.user_id
                 WHERE u.username = ?
                   AND u.password = ?
                 """, (username, password))

    row = crsr.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Incorrect login information!"}), 400

    user_id, face_blob, voice_blob = row

    face_result = compare_faces(bytes_to_image(face_blob), bytes_to_image(new_face.read()))
    if not bool(face_result['match']): return jsonify({"error": "Face Mismatch"}), 400

    voice_result = compare_voices(voice_blob, new_voice.read())
    if not bool(voice_result['match']): return jsonify({"error": "Voice Mismatch"}), 400

    return jsonify({"message": "Login successful"}), 200

#---------------------------END USER MANAGEMENT---------------------------


#---------------------------EMAIL VERIFICATIONS---------------------------

# send email with resend
@app.route("/api/send_email_verification", methods=["POST"])
def send_verification():
    data = request.get_json()
    email = data.get("email")
    code = str(random.randint(100000, 999999))

    conn = sqlite3.connect(DB_URL)
    crsr = conn.cursor()
    crsr.execute(
        "INSERT OR REPLACE INTO email_verification_codes (email, code) VALUES (?, ?)",
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

# check code from email
@app.route("/api/verify_email_code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    code = int(data.get("code"))
    conn = sqlite3.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT code FROM email_verification_codes WHERE email = ?", (email,)
    )
    row = cursor.fetchone()
    if row and int(row[0]) == code:
        cursor.execute("DELETE FROM email_verification_codes WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Verified!"}), 200
    conn.close()
    return jsonify({"error": "Invalid code"}), 401

#-------------------------END EMAIL VERIFICATIONS-------------------------


#----------------------------TEXT VERIFICATION----------------------------

# send text with vonage
@app.route("/api/send_text_verification", methods=["POST"])
def send_text_verification():
    data = request.get_json()
    phone = data.get("phone")

    sms_channel = SmsChannel(to=str(phone), from_=os.getenv("VONAGE_PHONE"))
    params = {
        'brand': 'Vonage',
        'workflow': [sms_channel],
    }
    verify_request = VerifyRequest(**params)

    response = vonage.verify.start_verification(verify_request)

    response_dict = json.loads(response.model_dump_json())

    conn = sqlite3.connect(DB_URL)
    crsr = conn.cursor()
    crsr.execute(
        "INSERT OR REPLACE INTO text_verification_codes (phone, request_id) VALUES (?, ?)",
        (phone, response_dict["request_id"])
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Code sent"}), 200

# check code from text
@app.route("/api/verify_text_code", methods=["POST"])
def verify_text_code():
    data = request.get_json()
    phone = data.get("phone")
    code = data.get("code")
    conn = sqlite3.connect(DB_URL)
    crsr = conn.cursor()
    crsr.execute(
        "SELECT request_id FROM text_verification_codes WHERE phone = ?", (phone,)
    )
    row = crsr.fetchone()

    if row:
        response = vonage.verify.check_code(request_id=str(row[0]), code=str(code))
        response_dict = json.loads(response.model_dump_json())

        if response_dict["status"] == 'completed':
            crsr.execute("DELETE FROM text_verification_codes WHERE phone = ?", (phone,))
            conn.commit()
            conn.close()
            return jsonify({"message": "Verified!"}), 200
    conn.close()
    return jsonify({"error": "Invalid code"}), 401

#--------------------------END TEXT VERIFICATION--------------------------



# @app.route("/api/get_voicedata/<username>", methods=["GET"])
# def get_voicedata(username):
#     conn = sqlite3.connect(sqliteurl)
#     cursor = conn.cursor()
#     cursor.execute("SELECT voicedata FROM users WHERE username = ?", (username,))
#     row = cursor.fetchone()
#     conn.close()
#     if row and row[0]:
#         return row[0], 200, {'Content-Type': 'audio/wav'}
#     else:
#         return jsonify({"error": "User not found or no voice data"}), 404
#
# @app.route("/api/get_imagedata/<username>", methods=["GET"])
# def get_imagedata(username):
#     conn = sqlite3.connect(sqliteurl)
#     cursor = conn.cursor()
#     cursor.execute("SELECT image FROM users WHERE username = ?", (username,))
#     row = cursor.fetchone()
#     conn.close()
#     if row and row[0]:
#         return row[0], 200, {'Content-Type': 'image/jpeg'}
#     else:
#         return jsonify({"error": "User not found or no image data"}), 404
#
# @app.route("/api/gemini", methods=["POST"])
# def gemini_prompt():
#     data = request.get_json()
#     if data is None:
#         return jsonify({"error": "Invalid JSON"}), 400
#     prompt = data.get("prompt")
#     response = client.models.generate_content(
#         model="gemini-2.0-flash", contents=prompt
#     )
#     return jsonify({"result": response.text}), 200