import subprocess as sp
import sys
import os
from time import sleep
from config import ADB_PATH

def check_apk_exists(apk_path: str):
    """
    Checks if the APK exists in the given path.

    Args:
        apk_path (str): Path to the APK file.
    """

    if not os.path.isfile(apk_path):
        raise RuntimeError(f"ERROR: APK file not found at {apk_path}.")

def check_emulator():
    """
    Checks if the emulator is running.
    """

    try:
        result = sp.run([ADB_PATH, "get-state"], stdout = sp.PIPE, stderr = sp.STDOUT, text = True) # "adb get-state"
        if result.stdout.strip() != "device": # "device" means the emulator is running
            connection.send(("current", "ERROR: No running emulator detected."))
            sys.exit(1)
    except sp.CalledProcessError as e:
        connection.send(("current", f"ERROR: Failed to execute 'adb get-state' for checking the emulator: {e.output}"))
        sys.exit(1)
    except Exception as e:
        connection.send(("current", f"ERROR: Unexpected failure while checking the emulator: {e}"))
        sys.exit(1)

def install_apk(apk_path: str):
    """
    Installs the APK on the emulator.

    Args:
        apk_path (str): Path to the APK file.
    """

    try:
        sp.run([ADB_PATH, "install", "-r", apk_path], stdout = sp.PIPE, stderr = sp.STDOUT, text = True, check = True)
    except sp.CalledProcessError as e:
        connection.send(("current", f"ERROR: Failed to execute 'adb install': {e.output}"))
        sys.exit(1)
    except Exception as e:
        connection.send(("current", f"ERROR: Unexpected failure while installing the APK: {e}"))
        sys.exit(1)

def launch_app(package_name: str):
    """
    Launches the installed app on the emulator.
    
    Args:
        package_name (str): Package name of the APK.
    """
    
    try:
        # Launches the app
        sp.run([ADB_PATH, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"], stdout = sp.PIPE, stderr = sp.STDOUT, text = True, check = True)
    except sp.CalledProcessError as e:
        connection.send(("current", f"ERROR: Failed to execute 'adb shell monkey': {e.output}"))
        sys.exit(1)
    except Exception as e:
        connection.send(("current", f"ERROR: Unexpected failure while launching the app: {e}"))
        sys.exit(1)

def check_installation(package_name: str):
    """
    Performs the installation check on the app.

    Args:
        package_name (str): Package name of the APK.
    """

    try:
        result = sp.run([ADB_PATH, "shell", "pm", "list", "packages"], stdout = sp.PIPE, stderr = sp.STDOUT, text = True, check = True)
        if package_name not in result.stdout:
            raise RuntimeError("ERROR: Package is NOT installed.")
    except sp.CalledProcessError as e:
        connection.send(("current", f"ERROR: Failed to execute 'adb shell pm list packages': {e.output}"))
        sys.exit(1)
    except Exception as e:
        connection.send(("current", f"ERROR: Unexpected failure while checking for installation: {e}"))
        sys.exit(1)

    connection.send(("current", "App is successfully installed."))

def check_crash_log(package_name: str):
    """
    Checks the crash logs if the app crashed.

    Args:
        package_name (str): Package name of the APK.

    Raises:
        RuntimeError: When the app crashes.
    """
    
    try:
        result = sp.run([ADB_PATH, "logcat", "-t", "0"], stdout = sp.PIPE, stderr = sp.STDOUT, text = True, check = True)
        logcat_output = result.stdout

        error_keywords = ["FATAL EXCEPTION", "has died", "crashed"]
        if any(
            line for line in logcat_output.splitlines()
            if any(keyword in line for keyword in error_keywords) and package_name in line
        ):
            raise RuntimeError("\nError: App crashed.\n")

    except sp.CalledProcessError as e:
        connection.send(("current", f"ERROR: Failed to execute 'adb logcat -t 0': {e.output}"))
        sys.exit(1)
    except Exception as e:
        connection.send(("current", f"ERROR: Unexpected failure while checking for crash logs: {e}"))
        sys.exit(1)

def check_app_pid(package_name: str):
    """
    Checks the process ID (PID) of the app.\n
    If it has no value, then it means the app isn't working.

    Args:
        package_name (str): Package name of the APK.
    """
    
    try:
        result = sp.run([ADB_PATH, "shell", "pidof", package_name], stdout = sp.PIPE, stderr = sp.STDOUT, text = True, check = False)
        pid = result.stdout.strip()
        if not pid: # No PID = App not running
            raise RuntimeError("\nError: App is not running.\n")
        else:
            connection.send(("current", "Health check passed."))
    except sp.CalledProcessError as e:
        connection.send(("current", f"ERROR: Failed to execute 'adb shell pidof': {e.output}"))
        sys.exit(1)
    except Exception as e:
        connection.send(("current", f"ERROR: Unexpected failure while checking for PID: {e}"))
        sys.exit(1)
    
# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
connection = None

def app_launch_main(apk_path: str, package_name: str, conn):
    """
    Installs, runs the app, and does the health check.

    Args:
        apk_path (str): APK path.
        package_name (str): Package name of the APK.
        conn (Connection): Pipe connection for sending data.
    """

    global connection
    connection = conn

    # Checks if APK file is there
    check_apk_exists(apk_path)

    # Ensures that the emulator is running
    check_emulator()

    # Installs the APK
    connection.send(("current", "Installing APK..."))
    install_apk(apk_path)

    # Launches the app
    connection.send(("current", "Launching app..."))
    launch_app(package_name)
    sleep(2) # Gives a little time for the app to launch completely

    # ///// Performs the health check /////
    # ----- Installation check -----
    check_installation(package_name)

    # ----- Running check -----
    # Checks for the crash in logcat
    check_crash_log(package_name)
    # Checks PID of the app
    check_app_pid(package_name)