from rich.live import Live
from rich.table import Table
from rich.console import Group
from rich.columns import Columns
from rich.text import Text

import multiprocessing as mp
import subprocess as sp
import threading as th
import os
import sys
import ast
import select
import tty, termios
from time import sleep
from virus_scan import vs_main
from test_apk import ta_main
from config import ERRORS_FILE, STATS_FILE

def key_listener():
    """
    Listens for 'q' key input from keyboard.
    """
    while True:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            key = sys.stdin.read(1)
            if key == 'q':
                user_triggered.set()

def check_ssh():
    """
    Checks if the SSH key is added to the agent.
    """

    result = sp.run(["ssh-add", "-l"], stdout = sp.PIPE, stderr = sp.DEVNULL)
    if result.returncode != 0:
        print("ERROR: SSH key is not added to the agent.")
        sys.exit(1)

def init_stats() -> tuple[dict, dict]:
    """
    Reads stats from the file. 
    If it doesn't exist, then initializes stats to default zeroed values.

    Returns:
        tuple:
            - **test_stats** (dict): Stats for APK Test.
            - **scan_stats** (dict): Stats for Virus Scan.
    """

    test_stats = {}
    scan_stats = {}

    if os.path.exists(STATS_FILE): # If the program has been launched before
        with open(STATS_FILE) as f:
            test_stats = ast.literal_eval(f.readline())
            scan_stats = ast.literal_eval(f.readline())
    else: # First launch
        test_stats = {        
            "current": "N/A",
            "counter": 1,
            "launched": 0,
            "crashed": 0,
            "not_installed": 0,
            "total": 0
        }
        
        scan_stats = {
            "current": "N/A",
            "counter": 1,
            "benign": 0,
            "suspicious": 0,
            "malicious": 0,
            "total": 0
        }

    return (test_stats, scan_stats)

def make_test_table(stats):
    """
    Writes down APK tester stats to the TUI.

    Args:
        stats (dict): test_apk.py stats.
    """
    
    table = Table(title = "APK tester")
    table.add_column("Metric")
    table.add_column("Value", width = 35)

    table.add_row("Current status:\n", str(stats.get("current", "N/A")))
    table.add_row("Apps launched:", str(stats.get("launched", "N/A")))
    table.add_row("Apps crashed:", str(stats.get("crashed", "N/A")))
    table.add_row("Apps not installed:", str(stats.get("not_installed", "N/A")))
    table.add_row("Total apks tested:", str(stats.get("total", "N/A")))
    return table

def make_scan_table(stats):
    """
    Writes down Virus Scanner stats to the TUI.

    Args:
        stats (dict): virus_scan.py stats.
    """

    table = Table(title = "Virus scanner")
    table.add_column("Metric")
    table.add_column("Value", width = 35)

    table.add_row("Current status:\n", str(stats.get("current", "N/A")))
    table.add_row("Benign (0 flags):", str(stats.get("benign", "N/A")))
    table.add_row("Suspicious (1 - 2 flags):", str(stats.get("suspicious", "N/A")))
    table.add_row("Malicious (2+ flags):", str(stats.get("malicious", "N/A")))
    table.add_row("Total apks scanned:", str(stats.get("total", "N/A")))
    return table

def tui(tui_at_conn, tui_vs_conn, test_stats: dict, scan_stats: dict):
    """
    Displays program statistics in a TUI (Text-based User Interface)

    Args:
        tui_at_conn (Connection): Connection pipe between APK tester and TUI.
        tui_vs_conn (Connection): Connection pipe between Virus Scanner and TUI.
        test_stats (dict): Stats for APK tester.
        scan_stats (dict): Stats for Virus Scanner.
    """

    finished = [False, False] # I - APK tester, II - Virus scanner
    status_message = Text("Press 'q' on keyboard to quit early.", style = "bold cyan")

    with Live("", refresh_per_second = 10) as live:
        while finished[0] == False or finished[1] == False:
            # 'q' key is pressed, requesting early exit
            if user_triggered.is_set():
                quit_flag.value = True
                status_message = Text("Quit request acknowledged. Waiting for programs to finish their current work...", style = "bold cyan")

            # APK Tester
            if not finished[0]:
                if tui_at_conn.poll(0.5): # Checks for sent data
                    key, value = tui_at_conn.recv() # Retrieves updated data
                    if value == "Finished testing all APKs." or value == "Exited early due to user request.":
                        finished[0] = True

                    test_stats[key] = value # Updates test stats

            # Virus Scanner
            if not finished[1]:
                if tui_vs_conn.poll(0.5):
                    key, value = tui_vs_conn.recv()
                    if value == "Finished scanning all APKs." or value == "Exited early due to user request.":
                        finished[1] = True

                    scan_stats[key] = value # Updates scan stats

            # Updates status message when programs are finished
            if finished[0] == True and finished[1] == True:
                if quit_flag.value == True: # Programs exited by the user request
                    status_message = Text("Stopped the execution early.", style = "bold cyan")
                else: # Programs finished their work
                    status_message = Text("Finished testing and scanning applications.", style = "bold cyan")

            live.update(Group(Columns([make_test_table(test_stats), make_scan_table(scan_stats)]), status_message))
            sleep(0.5)
    
    # Saves stats in a .txt file
    with open(STATS_FILE, "w") as f:
        f.write(f"{test_stats}\n" + 
        f"{scan_stats}")

# ////////////////////////////////////
# ///////// ENTRY POINT MAIN /////////
# ////////////////////////////////////

if __name__ == "__main__":
    # Writes all error logs to a file
    sys.stderr = open(ERRORS_FILE, "w")
    
    # Checks whether the SSH key is added to the agent
    check_ssh()

    # Activates thread that listens to keyboard inputs
    user_triggered = th.Event()
    th.Thread(target = key_listener, daemon = True).start()

    # Configures stdin to read single characters without having to press "Enter"
    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)

    # Creates pipes between tui and its child processes
    tui_vs_conn, vs_conn = mp.Pipe()
    tui_at_conn, at_conn = mp.Pipe()
    quit_flag = mp.Value('b', False)
    
    # Initializes stats
    test_stats, scan_stats = init_stats()

    # Creates the child processes and starts them
    ta = mp.Process(target = ta_main, args = (test_stats, at_conn, quit_flag))
    vs = mp.Process(target = vs_main, args = (scan_stats, vs_conn, quit_flag))
    ta.start()
    vs.start()

    # TUI 
    tui(tui_at_conn, tui_vs_conn, test_stats, scan_stats)

    # Restores original settings for stdin
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)