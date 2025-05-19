from rich.live import Live
from rich.table import Table
from rich.columns import Columns

import json
from time import sleep

def init_stats():
    """
    Resets stats.json to default zeroed values.
    """

    default_stats = {
        "test": {
            "current": "N/A",
            "launched": 0,
            "crashed": 0,
            "total": 0
        },
        "virus_scan": {
            "current": "N/A",
            "benign": 0,
            "suspicious": 0,
            "malicious": 0,
            "total": 0
        }
    }

    with open("stats.json", "w") as f:
        json.dump(default_stats, f, indent = 4)


def get_test_stats() -> dict:
    """
    Retrieves stats for test_apk.py.

    Returns:
        test_stats (JSON object): test_apk.py stats
    """

    try:
        with open("stats.json", "r") as f:
            result = json.load(f)
            return result.get("test")
    except Exception:
        return {}

def get_scan_stats() -> dict:
    """
        Retrieves stats for virus_scan.py.

        Returns:
            scan_stats (JSON object): virus_scan.py stats
    """

    try:
        with open("stats.json", "r") as f:
            result = json.load(f)
            return result.get("virus_scan")
    except Exception:
        return {}

def make_test_table(stats):
    """
    Writes down test_apk.py stats to the TUI

    Args:
        stats (JSON object): test_apk.py stats
    """
    
    table = Table(title = "APK testing stats")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Current status:", str(stats.get("current", "N/A")))
    table.add_row("Apps launched:", str(stats.get("launched", "N/A")))
    table.add_row("Apps crashed:", str(stats.get("crashed", "N/A")))
    table.add_row("Total apks tested:", str(stats.get("total", "N/A")))
    return table

def make_scan_table(stats):
    """
    Writes down virus_scan.py stats to the TUI

    Args:
        stats (JSON object): virus_scan.py stats
    """

    table = Table(title = "Virus Scan stats")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Current status:", str(stats.get("current", "N/A")))
    table.add_row("Benign:", str(stats.get("benign", "N/A")))
    table.add_row("Suspicious:", str(stats.get("suspicious", "N/A")))
    table.add_row("Malicious:", str(stats.get("malicious", "N/A")))
    table.add_row("Total apks scanned:", str(stats.get("total", "N/A")))
    return table

# ////////////////////////////////////
# /////////////// MAIN ///////////////
# ////////////////////////////////////

init_stats()

with Live(Columns([make_test_table({}), make_scan_table({})]), refresh_per_second = 2) as live:
    # while True:
    test_stats = get_test_stats()
    scan_stats = get_scan_stats()
    live.update(Columns([make_test_table(test_stats), make_scan_table(scan_stats)]))
    sleep(0.5)