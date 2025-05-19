import sqlite3
from datetime import datetime, timezone
    
def create_table(cursor):
    """
    Creates the `scan_results` table in the database if it doesn't exist.

    Args:
        cursor (any): Database cursor
    """

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS scan_results (" +
            "id INTEGER PRIMARY KEY AUTOINCREMENT," +
            "sha256_hash TEXT," +
            "positives INTEGER," +
            "total_engines INTEGER," +
            "scan_label TEXT," +
            "scan_time TEXT)"
    )

def insert_row(cursor, connection, data: dict):
    """
    Inserts a record to 'scan_results' table

    Args:
        cursor (cursor): Database cursor
        connection (connection): Database connection
        data (dict): The record
    """

    cursor.execute(
        "INSERT INTO scan_results (sha256_hash, positives, total_engines, scan_label, scan_time)" + 
        "VALUES (?, ?, ?, ?, ?)", 
            (data["sha256_hash"], data["positives"], 
            data["total_engines"], data["scan_label"], data["scan_time"]))
        
    connection.commit()

# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
def db_main(data):
    # Generates timestamp for scan
    scan_time = datetime.now(timezone.utc).isoformat()
    data["scan_time"] = scan_time

    # Connects or creates a database
    connection = sqlite3.connect("results.db")
    cursor = connection.cursor()

    # Creates a table (if doesn't exist)
    create_table(cursor)

    # Inserts the data for a file
    insert_row(cursor, connection, data)
    print("\nScan results were successfully added to the database.")

    # Closes connection
    connection.close()