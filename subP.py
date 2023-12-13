import sys
import select
import time

def check_for_command(timeout=1):
    """Check if there is a command available to read."""
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        return None

while True:
    command = check_for_command()
    if command == "pause":
        print("Subprocess paused.")
        while True:
            command = check_for_command()
            if command == "resume":
                print("Subprocess resumed.")
                break
    else:
        print("Subprocess running as usual.")
        # Perform regular subprocess task here
    time.sleep(1)
