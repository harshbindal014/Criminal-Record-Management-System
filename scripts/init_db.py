import sqlite3
import bcrypt
import os
from datetime import datetime

def init_database():
    """Initialize the database with required tables and default data"""
    # Create database directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('data/crime_records.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create criminals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS criminals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        crime_type TEXT,
        status TEXT,
        arrest_date DATE,
        image_path TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create cases table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_number TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT,
        date_reported DATE,
        closed_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create case_criminals table (for many-to-many relationship)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS case_criminals (
        case_id INTEGER,
        criminal_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (case_id, criminal_id),
        FOREIGN KEY (case_id) REFERENCES cases (id),
        FOREIGN KEY (criminal_id) REFERENCES criminals (id)
    )
    ''')
    
    # Create evidence table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER,
        name TEXT NOT NULL,
        type TEXT,
        status TEXT,
        collection_date DATE,
        collection_location TEXT,
        storage_location TEXT,
        image_path TEXT,
        description TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases (id)
    )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Hash the default password
        password = 'admin123'
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        ''', ('admin', hashed.decode('utf-8'), 'admin'))
    
    # Clear existing data before inserting new records
    cursor.execute('DELETE FROM case_criminals')
    cursor.execute('DELETE FROM evidence')
    cursor.execute('DELETE FROM cases')
    cursor.execute('DELETE FROM criminals')
    
    # Insert sample cases with recent dates
    cases = [
        ('Case-001', 'Robbery at Main Street Bank', 'Open', '2024-01-15', 'Bank robbery with armed suspects'),
        ('Case-002', 'Corporate Fraud Investigation', 'Open', '2024-02-20', 'Financial fraud in TechCorp'),
        ('Case-003', 'Downtown Assault', 'Closed', '2024-03-10', 'Bar fight resulting in serious injury'),
        ('Case-004', 'Mall Theft Ring', 'Open', '2024-01-25', 'Organized retail theft operation'),
        ('Case-005', 'Drug Distribution Network', 'Open', '2024-02-15', 'Interstate drug trafficking operation'),
        ('Case-006', 'Cyber Attack on City Systems', 'Open', '2024-03-05', 'Ransomware attack on municipal systems'),
        ('Case-007', 'Residential Burglary Spree', 'Closed', '2024-01-30', 'Series of home invasions'),
        ('Case-008', 'Company Embezzlement', 'Open', '2024-02-25', 'CFO embezzling company funds'),
        ('Case-009', 'Homicide Investigation', 'Open', '2024-03-15', 'Suspicious death in apartment'),
        ('Case-010', 'Child Abduction', 'Closed', '2024-01-20', 'Kidnapping of minor from school'),
        ('Case-011', 'Warehouse Arson', 'Open', '2024-02-10', 'Suspicious fire at storage facility'),
        ('Case-012', 'International Money Laundering', 'Open', '2024-03-20', 'Complex financial crime network'),
        ('Case-013', 'Business Extortion', 'Closed', '2024-01-10', 'Protection racket targeting local businesses'),
        ('Case-014', 'Identity Theft Ring', 'Open', '2024-02-05', 'Large-scale identity fraud operation'),
        ('Case-015', 'Organized Crime Investigation', 'Open', '2024-03-25', 'RICO case against crime family'),
        ('Case-016', 'Art Forgery Scheme', 'Closed', '2024-01-05', 'Counterfeit artwork sales'),
        ('Case-017', 'Public Property Vandalism', 'Open', '2024-02-15', 'Graffiti and property damage spree'),
        ('Case-018', 'Human Trafficking Ring', 'Open', '2024-03-10', 'International human smuggling operation'),
        ('Case-019', 'Terrorism Plot', 'Open', '2024-01-15', 'Prevention of planned terrorist attack'),
        ('Case-020', 'Prostitution Ring', 'Closed', '2024-02-20', 'Illegal brothel operation')
    ]
    cursor.executemany('''
        INSERT INTO cases (case_number, title, status, date_reported, description)
        VALUES (?, ?, ?, ?, ?)
    ''', cases)
    
    # Create directories for storing images
    os.makedirs('assets/images/criminals', exist_ok=True)
    os.makedirs('assets/images/evidence', exist_ok=True)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database() 