import sqlite3

def init_db():
    # Connects to or creates the database file
    conn = sqlite3.connect("dp_assessment.db")
    cursor = conn.cursor()
    
    # Creates the storage table for evaluations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supervisor_name TEXT NOT NULL,
            group_number TEXT NOT NULL,
            dp_part TEXT NOT NULL,
            report_number TEXT NOT NULL,
            s1_name TEXT NOT NULL,
            s1_raw INTEGER NOT NULL,
            s1_weighted REAL NOT NULL,
            s2_name TEXT NOT NULL,
            s2_raw INTEGER NOT NULL,
            s2_weighted REAL NOT NULL,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_number, dp_part, report_number)
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database created successfully!")