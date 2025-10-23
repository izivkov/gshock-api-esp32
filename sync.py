import os
import subprocess
import sys

# ---------------- Configuration ----------------
LOCAL_FOLDER = "."        # project root
ESP_ROOT = "/"            # ESP32 root

# Files/folders to ignore
IGNORE = {".git", ".vscode", "__pycache__", ".DS_Store"}
EXTENSIONS = {".py", ".mpy"}  # only copy these files

subprocess.run(["mpremote", "fs", "mkdir", "lib"])

# ---------------- Helper Functions ----------------
def list_local_files(directory):
    """Return list of local files to copy, relative to given directory."""
    local_files = []
    for root, dirs, files in os.walk(directory):
        # filter ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for f in files:
            if f in IGNORE:
                continue
            if os.path.splitext(f)[1] not in EXTENSIONS:
                continue
            rel_path = os.path.relpath(os.path.join(root, f), directory)
            local_files.append(rel_path.replace("\\", "/"))
    return local_files


def list_esp_files():
    """Return list of files on ESP32 (flattened)."""
    cmd = ["mpremote", "fs", "ls", "-r", ESP_ROOT]
    raw = subprocess.check_output(cmd).decode().splitlines()
    files = []
    for line in raw:
        line = line.strip()
        if not line or line.startswith("ls") or line.startswith("Directory"):
            continue
        # remove line numbers if present
        parts = line.split()
        if len(parts) > 1 and parts[0].isdigit():
            file_path = " ".join(parts[1:])
        else:
            file_path = line
        files.append(file_path.lstrip("/"))
    return files


def normalize(path):
    return path.lstrip("/").replace("\\", "/")

def delete_extra_files(local_files, esp_files):
    """Delete ESP32 files not present locally."""
    local_set = set(normalize(f) for f in local_files)
    for f in esp_files:
        f_norm = normalize(f)
        # ignore directories
        if f_norm.endswith("/"):
            continue
        if f_norm not in local_set:
            print(f"Deleting extra file on ESP32: {f_norm}")
            subprocess.run(["mpremote", "fs", "rm", f_norm])


def delete_extra_files_dry_run(local_files, esp_files, dry_run=True):
    local_set = set(normalize(f) for f in local_files)
    for f in esp_files:
        f_norm = normalize(f)
        if f_norm.endswith("/"):
            continue
        if f_norm not in local_set:
            print(f"[Dry-run] Would delete: {f_norm}" if dry_run else f"Deleting: {f_norm}")
            if not dry_run:
                subprocess.run(["mpremote", "fs", "rm", f_norm])


def copy_file(local_file):
    """Copy a single file to ESP32."""
    remote_path = os.path.join(ESP_ROOT, local_file).replace("\\", "/")
    remote_dir = os.path.dirname(remote_path)
    # create directory if needed
    if remote_dir != "/":
        subprocess.run(["mpremote", "fs", "mkdir", remote_dir])
    # copy file
    print(f"Copying {local_file} → {remote_path}")
    subprocess.run([
        "mpremote", "fs", "cp",
        local_file, ":" + remote_path
    ])


# ---------------- Main ----------------
def main():
    directory = LOCAL_FOLDER
    if len(sys.argv) > 1:
        directory = sys.argv[1]

    print(f"Listing local files in directory: {directory}")
    local_files = list_local_files(directory)
    print(f"{len(local_files)} local files to copy.")

    print("Listing ESP32 files...")
    esp_files = list_esp_files()
    print(f"{len(esp_files)} files on ESP32.")

    # Delete extra files
    delete_extra_files(local_files, esp_files)

    # Copy files one by one
    for f in local_files:
        copy_file(f)

    print("Sync complete!")


if __name__ == "__main__":
    main()
