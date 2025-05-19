import subprocess as sp
import sys
import csv

def retrieve_hash(app_number: int) -> str:
    """
    Opens the CSV file and retrieves the SHA-256 hash of the required APK file.
    
    Args:
        app_number (int): The app number from the list.
    Returns:
        sha256_hash (str): SHA-256 hash of the APK file.
    """

    try:
        with open('latest.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # Skips the header
            for i, row in enumerate(reader, 1):
                if i == app_number:
                    return row[0] # SHA-256 is in first column
    except FileNotFoundError:
        print("ERROR: 'latest.csv' file not found.")
        sys.exit(1)

def download_apk(app_number: int, apk_path: str) -> tuple[str, str]:
    """
    Downloads APK from AndroZoo using the provided SHA-256 hash.

    Args:
        app_number (int): Number of the app from the CSV file.
        apk_path (str): Output file path.

    Returns:
        tuple:
            - **sha256_hash** (str): SHA-256 hash of the APK.
            - **apk_path** (str): Output file path.
    """

    # Opens CSV file and returns the SHA-256 hash of the file
    sha256_hash = retrieve_hash(app_number)

    # Downloads the APK
    try:
        print(f"\n\nDownloading file {app_number}...")
        sp.check_call(f"echo {sha256_hash} | ssh -i ~/Desktop/ssh_key benoit@pierregraux.fr > {apk_path}", shell = True)
        return sha256_hash, apk_path
    except sp.CalledProcessError:
        print("ERROR: SSH command failed.")
        sys.exit(1)