from rich.live import Live
from rich.table import Table
from rich.columns import Columns

import multiprocessing as mp
import subprocess as sp
import os
import sys
from time import sleep
from virus_scan import vs_main
from test_apk import ta_main
from config import COMMANDS_FILE, STATS_FILE

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
    Initializes stats to default zeroed values.

    Returns:
        tuple:
            - **test_stats** (dict): Stats for APK Test.
            - **scan_stats** (dict): Stats for Virus Scan.
    """

    test_stats = {        
        "current": "N/A",
        "launched": 0,
        "crashed": 0,
        "total": 0
    }
    
    scan_stats = {
        "current": "N/A",
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
    table.add_column("Value")

    table.add_row("Current status:", str(stats.get("current", "N/A")))
    table.add_row("Apps launched:", str(stats.get("launched", "N/A")))
    table.add_row("Apps crashed:", str(stats.get("crashed", "N/A")))
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
    table.add_column("Value")

    table.add_row("Current status:", str(stats.get("current", "N/A")))
    table.add_row("Benign:", str(stats.get("benign", "N/A")))
    table.add_row("Suspicious:", str(stats.get("suspicious", "N/A")))
    table.add_row("Malicious:", str(stats.get("malicious", "N/A")))
    table.add_row("Total apks scanned:", str(stats.get("total", "N/A")))
    return table

def tui(tui_at_conn, tui_vs_conn, test_stats, scan_stats):
    """
    Displays program statistics in a TUI (Text-based User Interface)
    """

    finished = [False, False] # I - APK tester, II - Virus scanner

    with Live("", refresh_per_second = 2) as live:
        while finished[0] == False or finished[1] == False:
            # APK Tester
            if not finished[0]:
                if tui_at_conn.poll(0.5): # Checks for sent data
                    key, value = tui_at_conn.recv() # Retrieves updated data
                    if value == "Finished testing all APKs." or key == "counter":
                        finished[0] = True

                    test_stats[key] = value # Updates test stats

            # Virus Scanner
            if not finished[1]:
                if tui_vs_conn.poll(0.5):
                    key, value = tui_vs_conn.recv()
                    if value == "Finished scanning all APKs." or key == "counter":
                        finished[1] = True

                    scan_stats[key] = value # Updates scan stats

            live.update(Columns([make_test_table(test_stats), make_scan_table(scan_stats)]))
            sleep(0.5)
    
    if "counter" in test_stats and "counter" in scan_stats: # If counters were added to stats
        with open(STATS_FILE, "w") as f:
            f.write(f"APK_TESTER: {test_stats}\n" + 
            f"VIRUS_SCANNER: {scan_stats}")

# ////////////////////////////////////
# ///////// ENTRY POINT MAIN /////////
# ////////////////////////////////////

if __name__ == "__main__":
    # Launches user_input to allow the user to enter commands (like "quit")
    sp.Popen(["gnome-terminal", "--geometry=80x20", "--", "python3", "user_input.py"])

    # Checks whether the SSH key is added to the agent
    check_ssh()

    # Creates pipes between tui and its child processes
    tui_vs_conn, vs_conn = mp.Pipe()
    tui_at_conn, at_conn = mp.Pipe()
    
    # Creates the child processes and starts them
    vs = mp.Process(target = vs_main, args = (vs_conn,))
    ta = mp.Process(target = ta_main, args = (at_conn,))
    vs.start()
    ta.start()

    test_stats, scan_stats = init_stats()

    # TUI 
    tui(tui_at_conn, tui_vs_conn, test_stats, scan_stats)

    # Removes the temporary file for user commands
    if os.path.exists(COMMANDS_FILE):
        os.remove(COMMANDS_FILE)