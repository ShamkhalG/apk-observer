# Introduction
This program automates the testing and scanning of Android APK files. It consists of two main subprograms:
- **APK Tester**: Downloads APK files via the AndroZoo API, installs and executes them on an Android emulator. Then, it performs a health check on installed apps.
- **Virus Scanner**: Scans files for malicious characteristics using the VirusTotal API.

Program status, test and scan results are shown through a TUI (Text-based User Interface). In addition, the results are stored in a database for further analysis.

# Prerequisites
1. Download and install Android Studio must be installed on the computer.
2. Install 12 Android Virtual Devices with following names and Android versions:
- _**A4:** 4.4, **A5:** 5.1, **A6:** 6.0, **A7:** 7.1.1,_
- _**A8:** 8.1, **A9:** 9.0, **A10:** 10.0, **A11:** 11.0,_
- _**A12:** 12L, **A13:** 13.0, **A14:** 14.0, **A15:** 15.0_
3. Create an SSH key under the name **ssh_key** and store in **.ssh** directory. It's used to connect to the server to use Androzoo API.
4. Create an `.env` file in the project root directory with the following content:

```
API_KEY=*api_key*
API_SCAN_URL=*scan_url*
API_REPORT_URL=*report_url*

SSH_KEY_PATH=*path_to_ssh_key_located_in_.ssh_directory*
```
**Warning:** Do not put any spaces around = sign!

5. Install required dependencies using `pip install -r requirements.txt`.
6. Install SQLite Browser (optional, to view the database).

# Execution
1. Add the SSH key to the agent using `make ssh`. It reads the file **./ssh_key** located at the **.ssh** directory.
2. Start the program using `make run`. TUI will display the real-time statistics from both subprograms.

# Commands
- Adding SSH key (for current session): `make ssh`
- Execution: `make run`
- Cleaning generated files: `make clean`
- Viewing the database using SQLite Browser: `make db`

# Files
- **tui.py**  
Entry point of the program. It launches **APK Tester** and **Virus Scanner**, displaying their status and statistics in a TUI (Text-based User Interface). <br> It also listens for keyboard input - pressing `'q'` key sets a global `quit_flag` to terminate both processes early. When terminated, the current statistics are saved to a file. This allows the processes to resume from where they stopped during the next launch.
<br>
<br>

- **test_apk.py**  
Downloads APK files, launches emulators, runs and verifies apps, and updates the database for every tested APK.
- **downloader.py**  
Downloads APK files from Androzoo using SHA-256 hashes listed in `latest.csv`.
- **emu_manager.py**  
Starts or shuts down emulators based on the app's target SDK version.
- **app_launch.py**  
Installs and runs APKs on the emulator. Then, it performs the health check on the app.
- **db_manager.py**  
Adds the information about the APK to the database. In addition, information about scan results are retrieved from another table.
<br>
<br>

- **virus_scan.py**  
Downloads APKs and scans them for malicious behaviour using the *VirusTotal* API.
- **scan_db_manager.py**  
Adds scan results to the database.
<br>
<br>

- **config.py**  
Loads global settings and paths from `config.ini` and environment variables from `.env`.
- **stats.txt**  
Contains statistics of both programs that allow them to continue from where they stopped.
- **errors.txt**
Contains all error logs from the programs.

See the **Program Flow Diagram** section for an overview of how these files interact.

# Program Flow Diagram
![Program Flow Diagram](./diagram.png)