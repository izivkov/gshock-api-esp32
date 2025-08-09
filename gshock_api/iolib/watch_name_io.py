from gshock_api.casio_constants import CasioConstants  # If used elsewhere
from gshock_api.utils import clean_str, to_ascii_string, to_hex_string

from gshock_api.cancelable_result import CancelableResult

class WatchNameIO:
    result = None
    connection = None

    @staticmethod
    def request(connection):
        WatchNameIO.connection = connection
        WatchNameIO.result = CancelableResult()
        connection.request("23")  # Assuming this is non-blocking and triggers on_received later
        return WatchNameIO.result.get_result()

    @staticmethod
    def on_received(data):
        hex_str = to_hex_string(data)
        ascii_str = to_ascii_string(hex_str, 1)
        clean_data = clean_str(ascii_str)
        if WatchNameIO.result:
            WatchNameIO.result.set_result(clean_data)

    @staticmethod
    def send_to_watch():
        pass  # Implement as needed
