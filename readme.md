# Introduction
This project aims to automate the process of downloading APKs using AndroZoo API, downloading, installing, and executing them on an Android emulator.
The program also performs a health check on installed apps, scans files for malicious features on VirusTotal, and stores results in a database.
Current status and the statistics of the program are shown in a TUI (Text-based User Interface).

# Commands
- Execution: `make run`
- Adding SSH key: `make ssh`
- Cleaning generated files: `make clean`
- View the database using SQLite Browser: `make db`

# Files
There are 9 python files.

- **config.py**: Extracts global variables and configuration variables from `config.ini`.

- **tui.py:** Entry point of the program. It launches **APK Tester** and **Virus Scanner** and shows their current status as well as their statistics in a TUI (Text-based User Interface).

- **test_apk.py:** Downloads an APK file using `downloader.py`, launches emulator with `emu_manager.py`, runs and verifies the app on the emulator with `app_launch.py`, and updates the database with `db_manager.py` for every downloaded APK.
- **downloader.py**: Downloads APK files from Androzoo using the SHA-256 hash from `latest.csv`.
- **emu_manager.py:** Launches or shuts down emulators based on app's target SDK version.
- **app_launch.py:** Installs and runs the APK on the emulator. Then, it performs the health check on the app.
- **db_manager.py:** Adds the information about the APK to the database. In addition, information about scan results are retrieved from another table.

- **virus_scan.py:** Scans APK files for malicious activity on the *VirusTotal* website using their API.
- **scan_db_manager.py:** Adds scan results to the database.


# Program Flow Diagram
![Program Flow Diagram](./diagram.png)