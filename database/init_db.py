import sqlite3
import bcrypt
import os
from datetime import datetime
from utils.log_config import setup_logging

class DatabaseInitializer:
    def __init__(self):
        self.db_dir = 'data'
        self.db_path = os.path.join(self.db_dir, 'crime_records.db')
        self.logger = setup_logging('db_init')
        
    def init_database(self):
        """Initialize the database with required tables"""
        # Create database directory if it doesn't exist
        os.makedirs(self.db_dir, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if tables exist
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            tables_exist = cursor.fetchone() is not None
            
            if not tables_exist:
                # Create users table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
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
                    address TEXT,
                    contact_info TEXT,
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
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # Create case_criminals table
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
                    evidence_number TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT,
                    storage_location TEXT,
                    status TEXT,
                    notes TEXT,
                    date_collected DATE,
                    case_id INTEGER NOT NULL,
                    criminal_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases (id),
                    FOREIGN KEY (criminal_id) REFERENCES criminals (id)
                )
                ''')
                
                # Create default admin user
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
                    
                # Insert sample data only if tables were just created
                self.insert_sample_data(cursor)
            
            # Create directories for storing images (always ensure they exist)
            os.makedirs('assets/images/criminals', exist_ok=True)
            os.makedirs('assets/images/evidence', exist_ok=True)
            
            # Commit changes
            conn.commit()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise e
        finally:
            conn.close()
    
    def insert_sample_data(self, cursor):
        """Insert sample data into the database"""
        # Sample criminals data
        criminals = [
            ('James Wilson', 34, 'Male', 'Drug Trafficking', 'In Custody', '2024-01-15', '742 Pine Street', '555-0101', 'Leader of major drug distribution network'),
            ('Sarah Martinez', 29, 'Female', 'Drug Trafficking', 'In Custody', '2024-01-15', '123 Oak Lane', '555-0102', 'Key member of Wilson drug network'),
            ('Michael Chen', 31, 'Male', 'Drug Trafficking', 'In Custody', '2024-01-15', '456 Maple Ave', '555-0103', 'Distributor in Wilson network'),
            
            ('Robert Taylor', 45, 'Male', 'Fraud', 'Wanted', '2024-02-01', '789 Corporate Blvd', '555-0104', 'Mastermind of investment scheme'),
            ('Lisa Anderson', 38, 'Female', 'Fraud', 'In Custody', '2024-02-01', '321 Business Rd', '555-0105', 'CFO involved in corporate fraud'),
            ('David Miller', 41, 'Male', 'Fraud', 'Wanted', '2024-02-01', '654 Finance St', '555-0106', 'Investment advisor in fraud scheme'),
            
            ('Thomas Brown', 28, 'Male', 'Cybercrime', 'In Custody', '2024-02-15', '987 Tech Ave', '555-0107', 'Leader of ransomware group'),
            ('Emily White', 25, 'Female', 'Cybercrime', 'Wanted', '2024-02-15', '654 Digital Rd', '555-0108', 'Malware developer'),
            ('Daniel Lee', 30, 'Male', 'Cybercrime', 'In Custody', '2024-02-15', '321 Cyber St', '555-0109', 'Network infiltration specialist'),
            
            ('Christopher Davis', 39, 'Male', 'Robbery', 'In Custody', '2024-03-01', '147 Bank St', '555-0110', 'Leader of bank robbery crew'),
            ('Amanda Johnson', 32, 'Female', 'Robbery', 'In Custody', '2024-03-01', '258 Heist Rd', '555-0111', 'Getaway driver'),
            ('Kevin Thompson', 35, 'Male', 'Robbery', 'Wanted', '2024-03-01', '369 Crime Ave', '555-0112', 'Safe cracker'),
            
            ('William Harris', 52, 'Male', 'Money Laundering', 'In Custody', '2024-03-15', '741 Commerce St', '555-0113', 'International money laundering operation'),
            ('Maria Garcia', 44, 'Female', 'Money Laundering', 'Wanted', '2024-03-15', '852 Market Rd', '555-0114', 'Shell company operator'),
            ('John Murphy', 48, 'Male', 'Money Laundering', 'In Custody', '2024-03-15', '963 Trade Ave', '555-0115', 'Financial coordinator')
        ]
        
        cursor.executemany('''
            INSERT INTO criminals (name, age, gender, crime_type, status, arrest_date, address, contact_info, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', criminals)
        
        # Insert sample cases with recent dates
        cases = [
            ('Case-001', 'Robbery at Main Street Bank', 'Open', '2024-01-15', 'Bank robbery with armed suspects', 'Investigation ongoing'),
            ('Case-002', 'Corporate Fraud Investigation', 'Open', '2024-02-20', 'Financial fraud in TechCorp', 'Multiple suspects identified'),
            ('Case-003', 'Downtown Assault', 'Closed', '2024-03-10', 'Bar fight resulting in serious injury', 'Case resolved with arrest'),
            ('Case-004', 'Mall Theft Ring', 'Open', '2024-01-25', 'Organized retail theft operation', 'Surveillance footage under review'),
            ('Case-005', 'Drug Distribution Network', 'Open', '2024-02-15', 'Interstate drug trafficking operation', 'Multiple locations identified'),
            ('Case-006', 'Cyber Attack on City Systems', 'Open', '2024-03-05', 'Ransomware attack on municipal systems', 'Working with cybersecurity team'),
            ('Case-007', 'Residential Burglary Spree', 'Closed', '2024-01-30', 'Series of home invasions', 'All suspects apprehended'),
            ('Case-008', 'Company Embezzlement', 'Open', '2024-02-25', 'CFO embezzling company funds', 'Financial records under analysis'),
            ('Case-009', 'Homicide Investigation', 'Open', '2024-03-15', 'Suspicious death in apartment', 'Awaiting forensic results'),
            ('Case-010', 'Child Abduction', 'Closed', '2024-01-20', 'Kidnapping of minor from school', 'Child safely recovered'),
            ('Case-011', 'Warehouse Arson', 'Open', '2024-02-10', 'Suspicious fire at storage facility', 'Fire department report pending'),
            ('Case-012', 'International Money Laundering', 'Open', '2024-03-20', 'Complex financial crime network', 'International cooperation required'),
            ('Case-013', 'Business Extortion', 'Closed', '2024-01-10', 'Protection racket targeting local businesses', 'Ring leaders arrested'),
            ('Case-014', 'Identity Theft Ring', 'Open', '2024-02-05', 'Large-scale identity fraud operation', 'Multiple victims identified'),
            ('Case-015', 'Organized Crime Investigation', 'Open', '2024-03-25', 'RICO case against crime family', 'Building case evidence'),
            ('Case-016', 'Art Forgery Scheme', 'Closed', '2024-01-05', 'Counterfeit artwork sales', 'All artworks recovered'),
            ('Case-017', 'Public Property Vandalism', 'Open', '2024-02-15', 'Graffiti and property damage spree', 'Video evidence collected'),
            ('Case-018', 'Human Trafficking Ring', 'Open', '2024-03-10', 'International human smuggling operation', 'Multiple agencies involved'),
            ('Case-019', 'Terrorism Plot', 'Open', '2024-01-15', 'Prevention of planned terrorist attack', 'Heightened security measures'),
            ('Case-020', 'Prostitution Ring', 'Closed', '2024-02-20', 'Illegal brothel operation', 'Operation successfully shut down')
        ]
        
        cursor.executemany('''
            INSERT INTO cases (case_number, title, status, date_reported, description, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', cases)

        # Link criminals to their related cases - using case numbers for clarity
        case_criminals_data = [
            # Drug trafficking network (criminals 1-3)
            ('Case-005', 1), ('Case-005', 2), ('Case-005', 3),  # Drug Distribution Network case
            
            # Investment fraud scheme (criminals 4-6)
            ('Case-002', 4), ('Case-002', 5), ('Case-002', 6),  # Corporate Fraud Investigation
            ('Case-008', 5),                                     # Company Embezzlement
            
            # Cybercrime operation (criminals 7-9)
            ('Case-006', 7), ('Case-006', 8), ('Case-006', 9),  # Cyber Attack case
            
            # Bank robbery crew (criminals 10-12)
            ('Case-001', 10), ('Case-001', 11), ('Case-001', 12),  # Bank robbery case
            
            # Money laundering operation (criminals 13-15)
            ('Case-012', 13), ('Case-012', 14), ('Case-012', 15)  # International Money Laundering case
        ]
        
        # First get the case IDs by their case numbers
        for case_number, criminal_id in case_criminals_data:
            cursor.execute('SELECT id FROM cases WHERE case_number = ?', (case_number,))
            case_id = cursor.fetchone()[0]
            cursor.execute('''
                INSERT INTO case_criminals (case_id, criminal_id)
                VALUES (?, ?)
            ''', (case_id, criminal_id))

        # Insert related evidence for each case
        evidence = [
            # Drug trafficking evidence - Connected to Case 1 (Robbery at Main Street Bank) and Criminal 1 (James Wilson)
            (1, 1, 'DRUG-EV-001', 'Seized narcotics', 'Physical', '2024-01-15', 'Evidence locker A1', 'Secured', '10kg of cocaine seized from warehouse'),
            (1, 2, 'DRUG-EV-002', 'Financial records', 'Document', '2024-01-15', 'Digital storage', 'Processing', 'Bank statements and transaction records'),
            (1, 3, 'DRUG-EV-003', 'Surveillance footage', 'Digital', '2024-01-16', 'Digital storage', 'Analyzed', 'Warehouse surveillance recordings'),
            
            # Fraud evidence - Connected to Case 4 (Corporate Fraud Investigation) and related criminals
            (4, 4, 'FRAUD-EV-001', 'Investment documents', 'Document', '2024-02-01', 'Evidence room B2', 'Processing', 'Fraudulent investment certificates'),
            (4, 5, 'FRAUD-EV-002', 'Email correspondence', 'Digital', '2024-02-01', 'Digital storage', 'Analyzing', 'Emails between conspirators'),
            (5, 5, 'FRAUD-EV-003', 'Corporate records', 'Document', '2024-02-05', 'Evidence room B2', 'Secured', 'Falsified financial statements'),
            
            # Cybercrime evidence - Connected to Case 7 (Cyber Attack) and related criminals
            (7, 7, 'CYBER-EV-001', 'Server logs', 'Digital', '2024-02-15', 'Digital storage', 'Analyzing', 'Attack server access logs'),
            (7, 8, 'CYBER-EV-002', 'Malware samples', 'Digital', '2024-02-15', 'Secure storage', 'Analyzed', 'Captured ransomware samples'),
            (8, 9, 'CYBER-EV-003', 'Source code', 'Digital', '2024-02-20', 'Digital storage', 'Processing', 'Malware source code'),
            
            # Robbery evidence - Connected to Case 10 (Bank Robbery) and related criminals
            (10, 10, 'ROB-EV-001', 'Surveillance video', 'Digital', '2024-03-01', 'Digital storage', 'Analyzed', 'Bank security camera footage'),
            (10, 11, 'ROB-EV-002', 'Weapon', 'Physical', '2024-03-01', 'Evidence locker C3', 'Secured', 'Recovered firearm'),
            (10, 12, 'ROB-EV-003', 'Vehicle', 'Physical', '2024-03-01', 'Secure garage', 'Processing', 'Getaway vehicle'),
            
            # Money laundering evidence - Connected to Case 13 (Money Laundering) and related criminals
            (13, 13, 'ML-EV-001', 'Bank records', 'Document', '2024-03-15', 'Evidence room D1', 'Processing', 'International wire transfers'),
            (13, 14, 'ML-EV-002', 'Company documents', 'Document', '2024-03-15', 'Evidence room D1', 'Secured', 'Shell company registration papers'),
            (14, 15, 'ML-EV-003', 'Transaction logs', 'Digital', '2024-03-20', 'Digital storage', 'Analyzing', 'Suspicious transaction records')
        ]
        
        cursor.executemany('''
            INSERT INTO evidence (case_id, criminal_id, evidence_number, name, type, date_collected, storage_location, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', evidence)

if __name__ == "__main__":
    db_init = DatabaseInitializer()
    db_init.init_database()
    print("Database initialized successfully!") 