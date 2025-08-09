# alarms_io.py

import json
from gshock_api.alarms import alarms_inst, alarm_decoder
from gshock_api.cancelable_result import CancelableResult
from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class AlarmsIO:
    result = None
    connection = None

    @staticmethod
    def request(connection):
        AlarmsIO.connection = connection
        alarms_inst.clear()
        return AlarmsIO._get_alarms(connection)

    @staticmethod
    def _get_alarms(connection):
        AlarmsIO.result = CancelableResult()
        connection.sendMessage('{ "action": "GET_ALARMS"}')  # Assumes non-blocking
        return AlarmsIO.result.get_result()

    @staticmethod
    def send_to_watch(message=""):
        cmd1 = bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]])
        AlarmsIO.connection.write(0x000C, to_compact_string(to_hex_string(cmd1)))

        cmd2 = bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]])
        AlarmsIO.connection.write(0x000C, to_compact_string(to_hex_string(cmd2)))

    @staticmethod
    def send_to_watch_set(message):
        alarms_json_arr = json.loads(message).get("value")

        alarm_0 = alarms_inst.from_json_alarm_first_alarm(alarms_json_arr[0])
        casio0 = to_compact_string(to_hex_string(alarm_0))
        AlarmsIO.connection.write(0x000E, casio0)

        alarm_n = alarms_inst.from_json_alarm_secondary_alarms(alarms_json_arr)
        casio_n = to_compact_string(to_hex_string(alarm_n))
        AlarmsIO.connection.write(0x000E, casio_n)

    @staticmethod
    def on_received(data):
        decoded = alarm_decoder.to_json(to_hex_string(data))["ALARMS"]
        alarms_inst.add_alarms(decoded)

        if len(alarms_inst.alarms) == 5 and AlarmsIO.result:
            AlarmsIO.result.set_result(alarms_inst.alarms)
