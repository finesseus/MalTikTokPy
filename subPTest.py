import subprocess
import time

def start_subprocesses(num_processes):
    processes = []
    for i in range(num_processes):
        # Start a subprocess that reads from stdin
        with open(f'subpOutputs/{i}.txt', 'w+') as output_file:
            proc = subprocess.Popen(
                ["python3", "-u", "subP.py"],  # -u for unbuffered output
                stdin=subprocess.PIPE,
                text=True,
                stdout=output_file,
                stderr=subprocess.STDOUT
            )
        processes.append(proc)
    return processes

def send_command_to_subprocess(proc, command):
    print(f"Sending command to subprocess: {command}")
    proc.stdin.write(command + "\n")
    proc.stdin.flush()

def main():
    num_processes = 5
    processes = start_subprocesses(num_processes)
    last_command = 'resume'
    def new_command():
        thing = last_command
        last_command = 'pause ' if last_command == 'resume' else 'resume'
        return 'pause ' if thing == 'resume' else 'resume'
    input("should i pause?")

    for proc in processes:
        send_command_to_subprocess(proc, new_command())


if __name__ == "__main__":
    main()
