import subprocess as sp
import time
import sys
from config import ADB_PATH, EMULATOR_PATH

def choose_emulator(sdk_version: int) -> str:
    """
    Chooses which emulator is required for the APK based on its target on minimum SDK version.

    Args:
        sdk_version (int): Target or minimum SDK version.
    Returns:
        adv (str): Required emulator.
    """
    # Chooses correct emulator
    emulators = [
        (0, 19, "A4"),
        (21, 22, "A5"),
        (23, 23, "A6"),
        (24, 25, "A7"),
        (26, 27, "A8"),
        (28, 28, "A9"),
        (29, 29, "A10"),
        (30, 30, "A11"),
        (31, 32, "A12"),
        (33, 33, "A13"),
        (34, 34, "A14"),
        (35, 35, "A15"),
    ]
    
    required_avd = "A4" # Default emulator
    for min_sdk, target_sdk, emulator in emulators:
        if min_sdk <= sdk_version <= target_sdk:
            required_avd = emulator
    
    return required_avd

def get_devices() -> list[str]:
    """
    Obtains the list of running emulators.
    """

    result = sp.run([ADB_PATH, "devices"], stdout = sp.PIPE, stderr = sp.DEVNULL)
    output = result.stdout.decode().strip().splitlines()
    running_devices = [line.split()[0] for line in output[1:] if "emulator" in line] # Skips the first line: "List of devices attached"

    return running_devices

def wait_emulator_start(timeout: int = 300) -> bool:
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
            connection.send(("current", f"Warning: Failed to check\nemulator boot status: {e}"))
        time.sleep(2)

    return False

def start_emulator(avd: str):
    """
    Launches the correct emulator.

    Args:
        avd (str): Device to be launch.
    """

    connection.send(("current", f"Starting emulator '{avd}'..."))
    sp.Popen([EMULATOR_PATH, "-avd", avd, 
              "-wipe-data", "-no-snapshot-load", "-no-snapshot-save", "-no-boot-anim", 
              "-netdelay", "none", 
              "-netspeed", "full", "-gpu", "host", "-no-window"], stdout = sp.DEVNULL, stderr = sp.DEVNULL)

    if not wait_emulator_start():
        connection.send(("current", "Failed to launch emulator in time. Quitting."))
        sys.exit(1)

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
            connection.send(("current", f"Warning: Failed to check\nemulator shut down status: {e}"))
        time.sleep(1)
    return False

def shut_down_emulator():
    """
    Shuts down the running emulator.
    """
    
    running_devices = get_devices()
    device_serial = running_devices[0]

    connection.send(("current", f"Shutting down the emulator..."))
    sp.run([ADB_PATH, "-s", device_serial, "emu", "kill"], stdout = sp.DEVNULL, stderr = sp.DEVNULL)

    # Waits for the current emulator to shut down
    if not wait_emulator_shutdown(device_serial):
        connection.send(("current", "Timeout: Emulator did not shut down cleanly. Quitting."))
        sys.exit(1)

# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////
connection = None

def launch_emulator(sdk_version: int, conn):
    """
    Launches the Android emulator according to the target or minimum SDK version for the APK.

    Args:
        sdk_version (int): Target or minimum SDK version for the APK.
        conn (Connection): Pipe connection for sending data.
    """

    global connection
    connection = conn

    # Chooses right emulator for the APK
    required_avd = choose_emulator(sdk_version)
    
    # Starts the emulator
    start_emulator(required_avd)