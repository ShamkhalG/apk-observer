# Project introduction
This project aims to automate the process of downloading APKs using AndroZoo API, downloading, installing, and executing them.
The program also does a health check, checks for malicious features on VirusTotal, and stores results in a database.

# Commands
- Execution: `make run`
- Cleaning generated files: `make clean`
- View the database using SQLite Browser: `make db`

# Scripts
There are 10 python files.

- **main.py:** The entry point of the program. It downloads an APK file using `downloader.py`, launches emulator with `emu_manager.py`, runs the `app_launch.py` to verify the app on the emulator, and updates the database with `db_manager.py` for every downloaded APK.
- **config.py**: Stores global variables such as *adb*, *aapt*, and *emulator* paths.
- **downloader.py**: Downloads APK files from Androzoo using the SHA-256 hash from `latest.csv`.
- **emu_manager.py:** Launches or shuts down emulators based on app's target SDK version.
- **app_launch.py:** Installs and runs the APK on the emulator. Then, it performs the health check on the app.
- **virus_scan.py:** Shows scan results for the APK from VirusTotal website.
- **db_manager.py:** Adds the information about the APK to the database.

# Program Flow Diagram
![Program Flow Diagram](./diagram.png)