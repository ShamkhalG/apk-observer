import configparser

_config = configparser.ConfigParser()
_config.read("config.ini")

# Paths
EMULATOR_PATH = _config["paths"]["EMULATOR_PATH"]
ADB_PATH = _config["paths"]["ADB_PATH"]
AAPT_PATH = _config["paths"]["AAPT_PATH"]

# VirusTotal API parameters
API_KEY = _config["VirusTotal"]["API_KEY"]
API_SCAN_URL = _config["VirusTotal"]["API_SCAN_URL"]
API_REPORT_URL = _config["VirusTotal"]["API_REPORT_URL"]

# APK Test parameters
MAX_APK_NB = int(_config["APK_Test"]["MAX_APK_NB"])

# Virus Scan parameters
MAX_APK_NB_VS = int(_config["Virus_Scan"]["MAX_APK_NB_VS"])
MAX_ATTEMPT = int(_config["Virus_Scan"]["MAX_ATTEMPT"])
COOLDOWN = int(_config["Virus_Scan"]["COOLDOWN"])