import sqlite3
import face_recognition
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import tempfile
import os
from PIL import Image
import io
import secrets

# init tables
def setup_database(url):
    conn = sqlite3.connect(url)
    if not conn:
        return False

    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    crsr = conn.cursor()

    # clean out old sessions
    crsr.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")

    # create table users
    crsr.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        """
    )

    # create user data table
    crsr.execute(
        """
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
        
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            suffix TEXT,
            phone TEXT,
        
            address_line_1 TEXT,
            address_line_2 TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            sleep_coords TEXT,
        
            credit_card_number TEXT,
            expiration_month TEXT,
            expiration_year TEXT,
            cvc TEXT,
            social_security_number TEXT,
        
            license_plate TEXT,
            license_plate_state TEXT,
            date_of_birth TEXT,
            mothers_maiden_name TEXT,
            
            voice BLOB,
            face BLOB,
        
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """
    )

    # create table for email verification
    crsr.execute(
        """
        CREATE TABLE IF NOT EXISTS email_verification_codes (
            email TEXT PRIMARY KEY,
            code TEXT NOT NULL
        )
        """
    )

    # create table for phone verification
    crsr.execute(
        """
        CREATE TABLE IF NOT EXISTS text_verification_codes (
            phone TEXT PRIMARY KEY,
            request_id TEXT NOT NULL
        )
        """
    )

    # create session table
    crsr.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,          -- session token
            user_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    conn.commit()
    conn.close()

    return True

# facial comparison from images
def compare_faces(img1, img2):
    img1 = img1.convert('RGB')
    img2 = img2.convert('RGB')

    enc1 = face_recognition.face_encodings(np.array(img1))
    enc2 = face_recognition.face_encodings(np.array(img2))

    if not enc1:
        return {"error": "No face found in first image"}
    if not enc2:
        return {"error": "No face found in second image"}

    match = face_recognition.compare_faces([enc1[0]], enc2[0])[0]
    distance = face_recognition.face_distance([enc1[0]], enc2[0])[0]

    return {
        "match": match,
        "confidence_distance": float(distance)
    }

def bytes_to_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return image

# voice recognition

def bytes_to_wav_file(audio_bytes):
    temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp.write(audio_bytes)
    temp.close()
    return temp.name

def compare_voices(file1_bytes, file2_bytes, threshold=0.75):
    encoder = VoiceEncoder()

    wav1_path = bytes_to_wav_file(file1_bytes)
    wav2_path = bytes_to_wav_file(file2_bytes)

    try:
        emb1 = encoder.embed_utterance(preprocess_wav(wav1_path))
        emb2 = encoder.embed_utterance(preprocess_wav(wav2_path))


        similarity = float(
            np.dot(emb1, emb2) /
            (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        )

        return {
            "similarity": round(similarity, 3),
            "match": similarity >= threshold
        }

    finally:
        os.remove(wav1_path)
        os.remove(wav2_path)

# other utils ig idk

def generate_session_id():
    return secrets.token_urlsafe(64)