import os
import subprocess

print(f"Running script from: {os.path.abspath(__file__)}")

local_dir = os.path.expanduser("~/projects/gshock-api-esp32")
board_root = "/"
port = "/dev/ttyACM0"  # Your port

def list_local_py_files(base_dir):
    py_files = []
    print(f"Scanning local directory: {base_dir}")
    for root, dirs, files in os.walk(base_dir):
        print(f"Checking in {root}: files={files}")
        for f in files:
            if f.lower().endswith('.py'):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                print(f"Found local file: {rel_path}")
                py_files.append(rel_path)
    print(f"Total local .py files found: {len(py_files)}")
    return py_files

def list_board_py_files():
    print("Listing .py files on the board...")
    try:
        cmd = ["mpremote", "connect", port, "fs", "ls", "-r", board_root]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()

        py_files = []
        for line in lines:
            print("Splitting size from filename...")
            # Split line by whitespace, take the filename part only (everything after size)
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                size, filename = parts
                if filename.endswith(".py"):
                    py_files.append(filename)
                    print(f"Found on board: {filename}")

        print(f"Total board .py files found: {len(py_files)}")
        return py_files

    except subprocess.CalledProcessError as e:
        print("Error listing files on board:", e)
        print("Output:", e.output)
        return []

def upload_file(rel_path):
    local_path = os.path.join(local_dir, rel_path)
    board_path = ":" + rel_path.replace("\\", "/")  # Ensure remote path format

    # Extract directory part of remote path
    remote_dir = os.path.dirname(rel_path).replace("\\", "/")

    # If the file is inside a directory, create that directory on device first
    if remote_dir != "":
        print(f"Creating remote directory :{remote_dir} if it does not exist...")
        try:
            subprocess.run(["mpremote", "connect", port, "fs", "mkdir", f":{remote_dir}"], check=True)
        except subprocess.CalledProcessError as e:
            # mkdir fails if directory exists, this is okay
            print(f"Warning: Could not create directory :{remote_dir} (may already exist): {e}")

    print(f"Uploading {local_path} to {board_path}...")
    subprocess.run(["mpremote", "connect", port, "fs", "cp", local_path, board_path], check=True)

def delete_board_file(file_path):
    print(f"Deleting {file_path} from board...")
    try:
        subprocess.run(["mpremote", "connect", port, "fs", "rm", file_path], check=True)
        print("Delete success")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting {file_path}: {e}")

def sync():
    print("Starting sync process...")
    local_files = list_local_py_files(local_dir)
    board_files = list_board_py_files()

    # Upload or update local files
    for f in local_files:
        upload_file(f)

    # Remove files on board not in local
    for bf in board_files:
        if bf not in local_files:
            delete_board_file(bf)
    print("Sync process completed.")

if __name__ == "__main__":
    print(f"Starting...")
    sync()
