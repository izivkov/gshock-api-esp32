import sys
import subprocess

if len(sys.argv) != 2:
    print("Usage: python delete_dir.py <DIR_TO_DELETE>")
    sys.exit(1)

dir_to_delete = sys.argv[1]

micropython_code = f"""
import os
def rmtree(path):
    for fname in os.listdir(path):
        fpath = path + '/' + fname
        try:
            if (os.stat(fpath)[0] & 0x4000):
                rmtree(fpath)
                os.rmdir(fpath)
            else:
                os.remove(fpath)
        except OSError as e:
            print('Error removing', fpath, e)
rmtree('{dir_to_delete}')
"""

subprocess.run([
    "mpremote",
    "exec", micropython_code
])
