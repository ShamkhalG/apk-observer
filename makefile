clean: # Removes generated files
	rm ./test.apk ./scan.apk ./results.db

run: # Launches all programs
	python3 main.py

ssh: # Adds the SSH key to the terminal session
	ssh-add ~/Desktop/ssh_key

db: # Looks at the database
	sqlitebrowser results.db