import json
import os

class PersistentMap:
    def __init__(self, filepath):
        """
        Initialize the map and optionally load existing data from disk.
        """
        self.filepath = filepath
        self.data = {}
        self._load()

    def _file_exists(self, path):
        try:
            os.stat(path)
            return True
        except OSError:
            return False

    def _load(self):
        """
        Load the data from disk if the file exists.
        """
        try:
            if self._file_exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    self.data = json.load(f)
        except Exception as e:  # no JSONDecodeError in MicroPython
            print("⚠️ Failed to load map from {}: {}".format(self.filepath, e))
            self.data = {}

    def _save(self):
        """
        Save the current data to disk.
        """
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f)  # no indent in MicroPython
        except OSError as e:
            print("❌ Failed to save map to {}: {}".format(self.filepath, e))

    def add(self, key, value):
        """
        Add or update a key-value pair.
        """
        self.data[key] = value
        self._save()

    def delete(self, key):
        """
        Delete a key-value pair.
        """
        if key in self.data:
            del self.data[key]
            self._save()

    def clear(self):
        """
        Clear all key-value pairs.
        """
        self.data.clear()
        self._save()

    def get(self, key, default=None):
        """
        Get the value for a key, or return default.
        """
        return self.data.get(key, default)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

store = PersistentMap("gshock_server_data.json")
