#!/usr/bin/env python3

import sys
import time
import requests
from downloader import download_apk
from scan_db_manager import db_main
from config import API_KEY, API_SCAN_URL, API_REPORT_URL

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

    cur_attempt = 0
    max_attempt = 4


    while cur_attempt < max_attempt:
        try:
            response = requests.get(API_REPORT_URL, params = {'apikey': API_KEY, 'resource': sha256_hash}, timeout = 10)

            # 4 requests per minute limit is reached
            if response.status_code == 204:
                print("4 requests per minute limit hit. Waiting before retrying...")
                time.sleep(20)
                cur_attempt += 1
                continue

            # HTTP error
            if response.status_code != 200:
                print(f"HTTP error {response.status_code}: {response.text}")
                sys.exit(1)

            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            sys.exit(1)
    
    # 500 requests per day limit is reached
    print("ERROR: Maximum number of requests to VirusTotal per day has been reached. Terminating the program.")
    sys.exit(1)

def upload_file(apk_path: str):
    """
    Uploads a file to VirusTotal for later scan.

    Args:
        apk_path (str): Path to APK file.
    Returns:
        response (JSON object): Response in Pickle format.
    """

    print("File not found in Virus Total. Uploading for scan...")
    try:
        with open(apk_path, 'rb') as f:
            files = {'file': (apk_path, f)}
            response = requests.post(API_SCAN_URL, files = files, params = {'apikey': API_KEY}, timeout = 30)
            return response.json()
    except Exception as e:
        print(f"Upload failed: {e}", file=sys.stderr)
        sys.exit(1)

def scan_file(scan_id: str):
    """
    Waits for scan results and retrieves them.

    Args:
        scan_id (str): Scan ID.
    Returns:
        result (JSON object): Scan results.
    """

    print(f"Scan ID: {scan_id}")
    print("Waiting for scan results...")
    for attempt in range(12):  # Waits 60 seconds
        try:
            time.sleep(5)
            poll_response = requests.get(API_REPORT_URL, params={'apikey': API_KEY, 'resource': scan_id}, timeout = 10)
            report = poll_response.json()
            
            if report.get("response_code") == 1: # Scan completed
                return result
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Timed out waiting for scan results.")
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
positives = 0
total = 0
label = ""

MAX_APK_NB = 10
app_number = 1

while app_number <= MAX_APK_NB: # Temporary condition    
    # Retrieves the APK file from input
    sha256_hash, apk_path = download_apk(app_number, "scan.apk")

    # Checks if the file is already scanned in VirusTotal
    result = check_scan(sha256_hash)

    # File is not scanned
    if result.get("response_code") != 1:
        # Uploads the file for scanning
        upload_result = upload_file(apk_path)
        scan_id = upload_result.get("scan_id")
        if not scan_id:
            print("Failed to get scan ID.")
            sys.exit(1)
            
        # Waits for scan results and retrieves them
        result = scan_file(scan_id)
        
    positives = result.get("positives", 0)
    total = result.get("total", 0)
    label = get_label(positives)

    scan_data = {
        "sha256_hash": sha256_hash,
        "scan_label": label,
        "positives": positives,
        "total_engines": total,
    }

    # Updates the database
    db_main(scan_data)

    app_number += 1