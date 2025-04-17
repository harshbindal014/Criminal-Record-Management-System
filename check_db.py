import sqlite3
import os

def check_db():
    db_path = 'data/crime_records.db'
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check counts
    for table in [t[0] for t in tables]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")
        
    # Check case statuses
    cursor.execute("SELECT status, COUNT(*) FROM cases GROUP BY status")
    case_stats = cursor.fetchall()
    print("\nCase statuses:", case_stats)
    
    # Check crime types
    cursor.execute("SELECT crime_type, COUNT(*) FROM criminals GROUP BY crime_type")
    crime_stats = cursor.fetchall()
    print("\nCrime types:", crime_stats)
    
    conn.close()

if __name__ == "__main__":
    check_db() 