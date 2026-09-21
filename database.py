import sqlite3                                                  #SQLITE is the default built_in DB for python 
from datetime import datetime

DATABASE = "report.db"



def create_database():                                                      #to create the database 

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""                                                                              
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            original_file TEXT,
            generated_report TEXT
        )
    """)                                                                        #to create the table structure 

    conn.commit()

    conn.close()



def save_original_file(filename):                                                           #to save original file info 

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    date = datetime.now()

    cursor.execute("""
        INSERT INTO files (date, original_file)
        VALUES (?, ?)
    """, (date, filename))

    conn.commit()

    file_id = cursor.lastrowid

    conn.close()

    return file_id



def save_generated_report(file_id, filename):                              #to saves thee genrated_report 

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE files
        SET generated_report = ?
        WHERE id = ?
    """, (filename, file_id))

    conn.commit()

    conn.close()