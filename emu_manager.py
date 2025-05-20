import subprocess as sp
import time
import sys
from typing import Optional
from config import ADB_PATH, EMULATOR_PATH

def wait_emulator_launch(timeout: int = 300):
    """
    Waits for the emulator to fully boot by checking 'sys.boot_completed'.\n
    If the emulator doesn't launch in 5 minutes, the program terminates. 

    Args:
        timeout (int): Maximum time to wait in seconds.
    Returns:
        True/False (bool): True if boot completed, False if timeout exceeded.
    """

    start_time = time.time()
    sp.run([ADB_PATH, "wait-for-device"], stdout = sp.DEVNULL, stderr = sp.DEVNULL)
    while time.time() - start_time < timeout:
        try:
            result = sp.run([ADB_PATH, "shell", "getprop", "sys.boot_completed"], stdout = sp.PIPE, stderr = sp.DEVNULL, text = True)
            if result.stdout.strip() == "1":
                return True
        except Exception as e:
            connection.send(("current", f"Warning: Failed to check emulator boot status: {e}"))
        time.sleep(2)

    return False

def wait_emulator_shutdown(device_serial: str, timeout: int = 60) -> bool:
    """
    Waits for the given emulator to fully shut down.\n
    If the emulator doesn't shut down in 60 seconds, the program terminates.
    
    Args:
        device_serial (str): Emulator's serial number.
        timeout (int): Time limit for the emulator to shut down.
    Returns:
        True/False (bool): True if shut down, False if timeout is exceeded.
    """

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = sp.run([ADB_PATH, "devices"], stdout = sp.PIPE, stderr = sp.DEVNULL)
            output = result.stdout.decode().strip()
            if device_serial not in output:
                return True
        except Exception as e:
            connection.send(("current", f"Warning: Failed to check emulator shut down status: {e}"))
        time.sleep(1)
    return False

# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
connection = None

def launch_emulator(sdk_info: dict, conn):
    """
    Launches the Android emulator according to the target or minimum SDK version for the APK.

    Args:
        sdk_target (dict): SDK versions for the APK.
        conn (Connection): Pipe connection for sending data.
    """

    global connection
    connection = conn

    # Chooses correct emulator
    if (sdk_info["target"] is None and int(sdk_info["min"]) < 26) or (sdk_info["target"] is not None and int(sdk_info["target"]) < 26):
        avd = "Pixel_XL" # API 26, Android 8.0
    else:
        avd = "Pixel_XL_33" # API 33, Android 13.0
    

    # Checks connected emulator (if any)
    result = sp.run([ADB_PATH, "devices"], stdout = sp.PIPE, stderr = sp.DEVNULL)
    output = result.stdout.decode().strip().splitlines()

    # Skips the first line: "List of devices attached"
    running_devices = [line.split()[0] for line in output[1:] if "emulator" in line]

    if running_devices:
        device_serial = running_devices[0]

        # Checks running emulator's AVD name
        avd_name_result = sp.run([ADB_PATH, "-s", running_devices[0], "emu", "avd", "name"], stdout = sp.PIPE, stderr = sp.DEVNULL)
        running_avd = avd_name_result.stdout.decode().strip().splitlines()[0]

        if running_avd == avd: # Required emulator is already running
            connection.send(("current", f"Emulator '{avd}' is already running."))
            return
        else: # Required emulator is different, so shutting down the current one
            connection.send(("current", f"Different emulator '{running_avd}' is running. Shutting it down..."))
            sp.run([ADB_PATH, "-s", device_serial, "emu", "kill"])

            # Waits for the current emulator to shut down
            if not wait_emulator_shutdown(device_serial):
                connection.send(("current", "Timeout: Emulator did not shut down cleanly. Quitting."))
                sys.exit(1)
    
    # Starts the emulator
    connection.send(("current", f"Starting emulator '{avd}'..."))
    sp.Popen([EMULATOR_PATH, "-avd", avd, "-gpu", "host"], stdout = sp.DEVNULL, stderr = sp.DEVNULL)

    if not wait_emulator_launch():
        connection.send(("current", "Failed to launch emulator in time. Quitting."))
        sys.exit(1)