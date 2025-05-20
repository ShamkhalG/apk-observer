import subprocess as sp
import zipfile as zp

from emu_manager import launch_emulator
from downloader import download_apk
from app_launch import app_launch_main
from db_manager import db_main
from config import AAPT_PATH, MAX_APK_NB

def get_sdk_info() -> dict:
    """
    Retrieves and returns minimum, target, and maximum SDK versions of an apk.

    Returns:
        sdk_info (dict): SDK versions    
    """

    try:
        output = sp.check_output([AAPT_PATH, 'dump', 'badging', "./test.apk"], stderr = sp.DEVNULL)
        lines = output.decode().splitlines()

        sdk_info = {
            "min": None,
            "target": None,
            "max": None
        }

        for line in lines:
            if line.startswith("sdkVersion:"):
                sdk_info["min"] = line.split("'")[1]
            elif line.startswith("targetSdkVersion:"):
                sdk_info["target"] = line.split("'")[1]
            elif line.startswith("maxSdkVersion:"):
                sdk_info["max"] = line.split("'")[1]

        return sdk_info
    except sp.CalledProcessError:
        connection.send(("current", f"ERROR: Failed to retrieve SDK versions."))

def get_package_name(apk_path: str) -> str:
    """
    Retrieves the package name of the APK.

    Returns:
        package_name (str): Package name of the APK.
    """

    try:
        result = sp.run([AAPT_PATH, "dump", "badging", apk_path], stdout = sp.PIPE, stderr = sp.DEVNULL, check = True, text = True)
        for line in result.stdout.splitlines():
            if line.startswith("package:"):
                parts = line.split("'")
                return parts[1] # The package name
    except FileNotFoundError:
        raise RuntimeError("ERROR: APK file not found or invalid path.")
    except sp.CalledProcessError:
        raise RuntimeError("ERROR: Failed to extract package name with AAPT.")

def get_native_libs(apk_path: str) -> list[str] | list:
    """
    Retrieves native libraries that the app uses.

    Returns:
        One_of_Two:
            - **native_libs** (list[str]): Native libraries.
            - **empty_list** (list): If the app doesn't use any native libraries.
    """

    native_libs = []
    try:
        with zp.ZipFile(apk_path, 'r') as apk:
            for entry in apk.namelist():
                if entry.startswith("lib/") and entry.endswith(".so"):
                    native_libs.append(entry)
        return native_libs
    except FileNotFoundError:
        connection.send(("current", "ERROR: APK file not found."))
    except PermissionError:
        connection.send(("current", "ERROR: Permission denied to open the APK file."))
    except zp.BadZipFile:
        connection.send(("current", "ERROR: APK file is not a valid zip file."))

    return ["ERROR"]


# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
connection = None

def ta_main(conn):
    # Making the connection global to all functions
    global connection
    connection = conn

    app_number = 1

    while app_number <= MAX_APK_NB:
        try:
            # Downloads the APK
            apk_path = "test.apk"
            sha256_hash = download_apk(app_number, apk_path, connection)
            
            # Retrieves package name
            package_name = get_package_name(apk_path)

            # Retrieves SDK versions and shows them
            sdk_info = get_sdk_info()

            # Launches corresponding Android emulator
            launch_emulator(sdk_info, connection)

            # Installs, runs the app, and does the health check
            app_launch_main(apk_path, package_name, connection)

            # Retrieves native libraries that the app uses
            native_libs = get_native_libs(apk_path)

            data = {
                "apk_name": package_name,
                "sha256_hash": sha256_hash,
                "min_sdk_version": sdk_info["min"],
                "sdk_version": sdk_info["target"],
                "max_sdk_version": sdk_info["max"],
                "native_libs": ", ".join(native_libs) if native_libs else "", # If list is empty, put empty string
                "scan_label": "PENDING",
                "positives": "PENDING",
                "total_engines": "PENDING",
                "scan_time": "PENDING"
            }

            # Updates the database
            db_main(data, connection)

        except RuntimeError as e:
            connection.send(("current", e))
        finally:
            app_number += 1

    connection.send(("current", "Finished testing all APKs."))
    connection.close()