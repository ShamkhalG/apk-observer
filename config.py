import configparser

_config = configparser.ConfigParser()
_config.read("config.ini")

EMULATOR_PATH = _config["paths"]["emulator_path"]
ADB_PATH = _config["paths"]["adb_path"]
AAPT_PATH = _config["paths"]["aapt_path"]

API_KEY = _config["VirusTotal"]["API_KEY"]
API_SCAN_URL = _config["VirusTotal"]["API_SCAN_URL"]
API_REPORT_URL = _config["VirusTotal"]["API_REPORT_URL"]