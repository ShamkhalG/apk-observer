#!/usr/bin/env python3

import sys
import time
import requests
from downloader import download_apk
from scan_db_manager import db_main
from config import API_KEY, API_SCAN_URL, API_REPORT_URL, MAX_ATTEMPT, COOLDOWN, MAX_APK_NB_VS, COMMANDS_FILE

def check_scan(sha256_hash: str):
    """
    Checks if the file is already scanned in VirusTotal. Request limit handling:
    - If `4 requests per minute` limit is reached, it retries after 20 seconds.\n
    - If `500 requests per day` limit is reached, the program terminates.

    Program will make **4 attemps** to send the request. 
    \nIf they all fail, it means `500 requests per day` limit is reached.
    
    Args:
        sha256_hash (str): SHA-256 hash of the APK.
    Returns:
        response (JSON object): Response in Pickle format.
    """

    connection.send(("current", "Checking if the file has\nalready been scanned before..."))
    cur_attempt = 0
    while cur_attempt < MAX_ATTEMPT:
        try:
            response = requests.get(API_REPORT_URL, params = {'apikey': API_KEY, 'resource': sha256_hash}, timeout = 10)

            # 4 requests per minute limit is reached
            if response.status_code == 204:
                connection.send(("current", "4 requests per minute limit hit.\nWaiting before retrying..."))
                time.sleep(COOLDOWN)
                cur_attempt += 1
                continue

            # HTTP error
            if response.status_code != 200:
                connection.send(("current", f"HTTP error {response.status_code}: {response.text}"))
                sys.exit(1)

            connection.send(("current", "File has been already scanned.\nWriting down results..."))
            return response.json()
        except requests.RequestException as e:
            connection.send(("current", f"ERROR: Request to Virus Total failed: {e}"))
            sys.exit(1)
    
    # 500 requests per day limit is reached
    connection.send(("current", "ERROR: Maximum number of requests per day\nto VirusTotal has been reached. Quitting."))
    sys.exit(1)

def upload_file(apk_path: str):
    """
    Uploads a file to VirusTotal for later scan.

    Args:
        apk_path (str): Path to APK file.
    Returns:
        response (JSON object): Response in Pickle format.
    """

    connection.send(("current", "File not found in Virus Total.\nUploading for scan..."))
    try:
        with open(apk_path, 'rb') as f:
            files = {'file': (apk_path, f)}
            response = requests.post(API_SCAN_URL, files = files, params = {'apikey': API_KEY}, timeout = 30)
            return response.json()
    except Exception as e:
        raise RuntimeError(f"ERROR: Upload failed: {e}")

def scan_file(scan_id: str):
    """
    Waits for scan results and retrieves them.

    Args:
        scan_id (str): Scan ID.
    Returns:
        result (JSON object): Scan results.
    """

    connection.send(("current", "Waiting for scan results..."))
    for _ in range(12):  # Waits 60 seconds
        try:
            time.sleep(5)
            poll_response = requests.get(API_REPORT_URL, params = {'apikey': API_KEY, 'resource': scan_id}, timeout = 10)
            report = poll_response.json()
            
            if report.get("response_code") == 1: # Scan completed
                return report
        except Exception as e:
            raise RuntimeError(f"ERROR: in scan_file: {e}")
    else:
        connection.send(("current", "ERROR: Timed out waiting for scan results."))
        sys.exit(1)

def get_label(positives: int) -> str:
    """
    Marks an application based on the scan results.

    Args:
        positives (int): Number of engines that marked the apk as malicious.
    Returns:
        label (str): App label.
    """

    if positives == 0:
        return "BENIGN"
    elif positives <= 2:
        return "SUSPICIOUS"
    else:
        return "MALICIOUS"

# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
connection = None

def vs_main(conn, quit_flag: bool):
    # Making the connection global to all functions
    global connection
    connection = conn

    # Stats
    stats = {
        "app_number": 1,
        "benign": 0,
        "suspicious": 0,
        "malicious": 0,
        "total": 0
    }

    while stats["app_number"] <= MAX_APK_NB_VS:
        try:
            # Checks if the quit flag is triggered
            if quit_flag.value == True:
                connection.send(("current", "Exited early due to user request."))
                connection.send(("counter", stats["app_number"])) # Sends the stats["app_number"] to save it
                break

            # Retrieves the APK file from input
            apk_path = "scan.apk"
            sha256_hash = download_apk(stats["app_number"], apk_path, connection)

            # Checks if the file is already scanned in VirusTotal
            result = check_scan(sha256_hash)

            # File is not scanned
            if result.get("response_code") != 1:
                # Uploads the file for scanning
                upload_result = upload_file(apk_path)
                scan_id = upload_result.get("scan_id")
                if not scan_id:
                    connection.send(("current", "ERROR: Failed to get scan ID."))
                    sys.exit(1)
                    
                # Waits for scan results and retrieves them
                result = scan_file(scan_id)
                
            positives = result.get("positives", 0)
            total = result.get("total", 0)
            label = get_label(positives)

            # Updates stats
            stats[label.lower()] += 1
            connection.send((label.lower(), stats[label.lower()]))
            stats["total"] += 1
            connection.send(("total", stats["total"]))

            scan_data = {
                "sha256_hash": sha256_hash,
                "scan_label": label,
                "positives": positives,
                "total_engines": total,
            }

            # Updates the database
            db_main(scan_data, connection)
        except RuntimeError as e:
            connection.send(("current", e))
        finally:
            stats["app_number"] += 1
    
    connection.send(("current", "Finished scanning all APKs."))
    connection.close()