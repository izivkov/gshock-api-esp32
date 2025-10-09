import ujson as json

# {
#     "ssid": "MyWiFi",
#     "password": "MySecretPass",
#     "timezone": "America/Toronto"
# }

class ConfigManager:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = {}

    def get_instructions(self):

        return """

        Configuration file not found or invalid. We need to configure a WiFi connection,
        so the device will obtain network time.

        Please create a configuration file "config.json" with the following structure:

        {
            "ssid": "YourWiFiSSID",
            "password": "YourWiFiPassword",
            "timezone": "YourTimezone"
        }

        (timezone has to be in the format "Continent/City", i.e. "America/Toronto").
        Edit it with the correct values and copy this file to your device:

            mpremote connect /dev/ttyACM0 fs cp config.json :config.json

        Restart the app.
        """

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.config = json.load(f)
        except OSError:
            print("Config file not found, using defaults")
            self.config = {}
        except ValueError:
            print("Config file corrupt, resetting")
            self.config = {}

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.config, f)
            print("Config saved")
        except Exception as e:
            print("Failed to save config:", e)

    def set(self, key, value):
        self.config[key] = value

    def get(self, key, default=None):
        return self.config.get(key, default)

config_manager = ConfigManager()