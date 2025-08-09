from gshock_api.casio_constants import CasioConstants
from gshock_api.cancelable_result import CancelableResult

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class WorldCitiesIO:
    result = None
    connection = None

    def __init__(self):
        pass

    def request(self, connection, city_number):
        WorldCitiesIO.connection = connection
        key = "1f0{}".format(city_number)

        connection.request(key)
        WorldCitiesIO.result = CancelableResult()
        return WorldCitiesIO.result.get_result()

    def send_to_watch(self, connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_WORLD_CITIES"]]))

    def on_received(self, data):
        if WorldCitiesIO.result:
            WorldCitiesIO.result.set_result(data)
