import sqlite3
import face_recognition
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
import tempfile
import os
import subprocess
from pathlib import Path

# init tables
def setup_database(url):
    conn = sqlite3.connect(url)
    if not conn:
        return False

    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")

    crsr = conn.cursor()

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
        
            credit_card_number TEXT,
            expiration_month TEXT,
            expiration_year TEXT,
            cvc TEXT,
            social_security_number TEXT,
        
            license_plate TEXT,
            license_plate_state TEXT,
            date_of_birth TEXT,
            mothers_maiden_name TEXT,
        
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

# voice recognition
def compare_voices(file1, file2, threshold=0.75):
    encoder = VoiceEncoder()

    # Convert webm → wav
    wav1 = convert_webm_to_wav(file1)
    wav2 = convert_webm_to_wav(file2)

    try:
        emb1 = encoder.embed_utterance(preprocess_wav(Path(wav1)))
        emb2 = encoder.embed_utterance(preprocess_wav(Path(wav2)))

        similarity = float(
            np.dot(emb1, emb2) /
            (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        )

        return {
            "similarity": round(similarity, 3),
            "match": similarity >= threshold
        }

    finally:
        # Cleanup temp files
        os.remove(wav1)
        os.remove(wav2)

def convert_webm_to_wav(input_path: str) -> str:
    """
    Converts a .webm file to a temporary 16kHz mono WAV file.
    Returns the path to the WAV file.
    """
    tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_wav.close()

    command = [
        "ffmpeg",
        "-y",                     # overwrite if exists
        "-i", input_path,
        "-ac", "1",               # mono
        "-ar", "16000",           # 16kHz
        tmp_wav.name
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tmp_wav.name
