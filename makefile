clean: # Removes generated files
	rm ./test.apk ./scan.apk ./results.db

run: # Launches all programs
	@python3 test_apk.py & \
	python3 virus_scan.py & \
	python3 tui.py

test: # Launches APK tester
	python3 test_apk.py

scan: # Launches virus scanner program
	python3 virus_scan.py

tui:
	python3 tui.py

ssh: # Adds the SSH key to the terminal session
	ssh-add ~/Desktop/ssh_key

db: # Looks at the database
	sqlitebrowser results.db