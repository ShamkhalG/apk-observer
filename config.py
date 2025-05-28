from dotenv import load_dotenv
import configparser
import os

load_dotenv()

_config = configparser.ConfigParser()
_config.read("config.ini")

# Paths
EMULATOR_PATH = os.path.expanduser(_config["Paths"]["EMULATOR_PATH"])
ADB_PATH = os.path.expanduser(_config["Paths"]["ADB_PATH"])
AAPT_PATH = os.path.expanduser(_config["Paths"]["AAPT_PATH"])

# VirusTotal API parameters
API_KEY = os.getenv("API_KEY")
API_SCAN_URL = _config["API_URLs"]["API_SCAN_URL"]
API_REPORT_URL = _config["API_URLs"]["API_REPORT_URL"]

# SSH key path
SSH_KEY_PATH = os.path.expanduser(os.getenv("SSH_KEY_PATH"))

# Files
STATS_FILE = _config["Files"]["STATS_FILE"]
ERRORS_FILE = _config["Files"]["ERRORS_FILE"]

# APK Test parameters
MAX_APK_NB_TA = int(_config["APK_Test"]["MAX_APK_NB_TA"])

# Virus Scan parameters
MAX_APK_NB_VS = int(_config["Virus_Scan"]["MAX_APK_NB_VS"])
MAX_ATTEMPT = int(_config["Virus_Scan"]["MAX_ATTEMPT"])
COOLDOWN = int(_config["Virus_Scan"]["COOLDOWN"])

# Timeout for file downloader
TIMEOUT = int(_config["Downloader"]["TIMEOUT"])