clean: # Removes generated files
	rm ./test.apk ./scan.apk ./results.db ./stats.txt ./errors.txt

run: # Launches all programs
	python3 tui.py

ssh: # Adds the SSH key to the terminal session
	ssh-add ~/.ssh/ssh_key

db: # Looks at the database
	sqlitebrowser results.db