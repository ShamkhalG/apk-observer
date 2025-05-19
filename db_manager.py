import sqlite3
from datetime import datetime, timezone
    
def create_table(cursor):
    """
    Creates a table in the database if it doesn't exist.

    Args:
        cursor (any): Database cursor
    """

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS apk_info (" +
            "id INTEGER PRIMARY KEY AUTOINCREMENT," +
            "apk_name TEXT," +
            "sha256_hash TEXT," +
            "min_sdk_version TEXT," +
            "sdk_version TEXT," +
            "max_sdk_version TEXT," +
            "native_libs TEXT," +
            "scan_label TEXT," +
            "positives INTEGER," +
            "total_engines INTEGER," +
            "test_time TEXT," +
            "scan_time TEXT)"
    )

def insert_row(cursor, connection, data: dict):
    """
    Inserts a record to 'apk_info' table

    Args:
        cursor (cursor): Database cursor
        connection (connection): Database connection
        data (dict): The record
    """

    cursor.execute(
        "INSERT INTO apk_info (apk_name, sha256_hash, min_sdk_version, sdk_version, max_sdk_version," + 
        "native_libs, scan_label, positives, total_engines, test_time, scan_time)" + 
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (data["apk_name"], data["sha256_hash"], data["min_sdk_version"], 
            data["sdk_version"], data["max_sdk_version"], data["native_libs"], 
            data["scan_label"], data["positives"], data["total_engines"], 
            data["test_time"], data["scan_time"]))
        
    connection.commit()

def insert_scan_results(cursor, connection, sha256_hash: str):
    """
    Inserts scan results for the app from 'scan_results' to 'apk_info' table

    Args:
        cursor (cursor): Database cursor
        connection (connection): Database connection
        sha256_hash (str): SHA-256 hash of the file
    """

    cursor.execute(
        """
        UPDATE apk_info
        SET 
            scan_label = scan_results.scan_label,
            positives = scan_results.positives,
            total_engines = scan_results.total_engines,
            scan_time = scan_results.scan_time
        FROM scan_results
        WHERE apk_info.sha256_hash = scan_results.sha256_hash
        AND apk_info.sha256_hash = ?;
        """,
        (sha256_hash,))

    connection.commit()

# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
def db_main(data):
    # Generates timestamp for test
    test_time = datetime.now(timezone.utc).isoformat()
    data["test_time"] = test_time

    # Connects or creates a database
    connection = sqlite3.connect("results.db")
    cursor = connection.cursor()

    # Creates a table (if doesn't exist)
    create_table(cursor)

    # Inserts the data for a file
    insert_row(cursor, connection, data)
    print("\nAPK information was successfully added to the database.")

    # Inserts scan results of the APK
    insert_scan_results(cursor, connection, data["sha256_hash"])

    # Closes connection
    connection.close()