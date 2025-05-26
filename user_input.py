from config import COMMANDS_FILE

with open(COMMANDS_FILE, "w") as f:
    command = ""
    while command != "quit":
        print("\nAvailable commands: quit - To shutdown the program right now.")
        command = input("Command: ")
    f.write(command)