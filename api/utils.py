import sqlite3


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