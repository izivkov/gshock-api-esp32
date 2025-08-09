import uasyncio as asyncio
import ujson as json
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger
from gshock_api.casio_constants import CasioConstants

from gshock_api.utils import (
    clean_str,
    dec_to_hex,
    to_ascii_string,
    to_byte_array,
    to_compact_string,
    to_hex_string,
    to_int_array,
)

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class ReminderMasks:
    YEARLY_MASK = 0b00001000
    MONTHLY_MASK = 0b00010000
    WEEKLY_MASK = 0b00000100

    SUNDAY_MASK = 0b00000001
    MONDAY_MASK = 0b00000010
    TUESDAY_MASK = 0b00000100
    WEDNESDAY_MASK = 0b00001000
    THURSDAY_MASK = 0b00010000
    FRIDAY_MASK = 0b00100000
    SATURDAY_MASK = 0b01000000

    ENABLED_MASK = 0b00000001


class EventsIO:
    result = None
    connection = None
    title = None

    @staticmethod
    async def request(connection, event_number):
        EventsIO.connection = connection
        await connection.request("30{}".format(event_number))
        await connection.request("31{}".format(event_number))
        EventsIO.result = CancelableResult()
        return EventsIO.result.get_result()

    @staticmethod
    async def send_to_watch_set(message):
        def reminder_title_from_json(reminder_json):
            title_str = reminder_json.get("title")
            return to_byte_array(title_str, 18)

        def reminder_time_from_json(reminder_json):
            def create_time_detail(repeat_period, start_date, end_date, days_of_week):
                def encode_date(time_detail, start_date, end_date):
                    def string_to_month(month_str):
                        months = {
                            "january": 1,
                            "february": 2,
                            "march": 3,
                            "april": 4,
                            "may": 5,
                            "june": 6,
                            "july": 7,
                            "august": 8,
                            "september": 9,
                            "october": 10,
                            "november": 11,
                            "december": 12,
                        }
                        return months.get(month_str.lower(), 1)

                    def hex_to_dec(hex_val):
                        return int(str(hex_val), 16)

                    time_detail[0] = hex_to_dec(start_date["year"] % 2000)
                    time_detail[1] = hex_to_dec(string_to_month(start_date["month"]))
                    time_detail[2] = hex_to_dec(start_date["day"])
                    time_detail[3] = hex_to_dec(end_date["year"] % 2000)
                    time_detail[4] = hex_to_dec(string_to_month(end_date["month"]))
                    time_detail[5] = hex_to_dec(end_date["day"])
                    time_detail[6], time_detail[7] = 0, 0

                time_detail = [0] * 8

                if repeat_period == "NEVER":
                    encode_date(time_detail, start_date, end_date)
                elif repeat_period == "WEEKLY":
                    encode_date(time_detail, start_date, end_date)
                    day_of_week = 0
                    if days_of_week:
                        for day in days_of_week:
                            if day == "SUNDAY": day_of_week |= ReminderMasks.SUNDAY_MASK
                            elif day == "MONDAY": day_of_week |= ReminderMasks.MONDAY_MASK
                            elif day == "TUESDAY": day_of_week |= ReminderMasks.TUESDAY_MASK
                            elif day == "WEDNESDAY": day_of_week |= ReminderMasks.WEDNESDAY_MASK
                            elif day == "THURSDAY": day_of_week |= ReminderMasks.THURSDAY_MASK
                            elif day == "FRIDAY": day_of_week |= ReminderMasks.FRIDAY_MASK
                            elif day == "SATURDAY": day_of_week |= ReminderMasks.SATURDAY_MASK
                    time_detail[6] = day_of_week
                elif repeat_period in ("MONTHLY", "YEARLY"):
                    encode_date(time_detail, start_date, end_date)
                else:
                    logger.debug("Cannot handle Repeat Period: {}".format(repeat_period))

                return time_detail

            def create_time_period(enabled, repeat_period):
                time_period = 0
                if enabled:
                    time_period |= ReminderMasks.ENABLED_MASK
                if repeat_period == "WEEKLY":
                    time_period |= ReminderMasks.WEEKLY_MASK
                elif repeat_period == "MONTHLY":
                    time_period |= ReminderMasks.MONTHLY_MASK
                elif repeat_period == "YEARLY":
                    time_period |= ReminderMasks.YEARLY_MASK
                return time_period

            enabled = reminder_json.get("enabled")
            repeat_period = reminder_json.get("repeat_period")
            start_date = reminder_json.get("start_date")
            end_date = reminder_json.get("end_date")
            days_of_week = reminder_json.get("days_of_week")

            reminder_cmd = bytearray()
            reminder_cmd.append(create_time_period(enabled, repeat_period))
            reminder_cmd.extend(create_time_detail(repeat_period, start_date, end_date, days_of_week))

            return reminder_cmd

        reminders_json_arr = json.loads(message).get("value")
        for index, element in enumerate(reminders_json_arr):
            title = reminder_title_from_json(element)

            title_byte_arr = bytearray([CHARACTERISTICS["CASIO_REMINDER_TITLE"], index + 1])
            title_byte_arr.extend(title)
            title_hex = to_compact_string(to_hex_string(title_byte_arr))
            await EventsIO.connection.write(0x000E, title_hex)

            reminder_time_byte_arr = bytearray([
                CHARACTERISTICS["CASIO_REMINDER_TIME"], index + 1
            ])
            reminder_time_byte_arr.extend(reminder_time_from_json(element.get("time")))
            time_hex = to_compact_string(to_hex_string(reminder_time_byte_arr))
            await EventsIO.connection.write(0x000E, time_hex)

    @staticmethod
    def on_received_title(message):
        EventsIO.title = ReminderDecoder.reminder_title_to_json(message)

    @staticmethod
    def on_received(message):
        data = to_hex_string(message)

        def decode_time_period(tp):
            enabled = bool(tp & ReminderMasks.ENABLED_MASK)
            if tp & ReminderMasks.WEEKLY_MASK: repeat = "WEEKLY"
            elif tp & ReminderMasks.MONTHLY_MASK: repeat = "MONTHLY"
            elif tp & ReminderMasks.YEARLY_MASK: repeat = "YEARLY"
            else: repeat = "NEVER"
            return enabled, repeat

        def decode_date(td):
            months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
                      "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
            return {
                "year": dec_to_hex(td[0]) + 2000,
                "month": months[dec_to_hex(td[1]) - 1],
                "day": dec_to_hex(td[2])
            }

        def decode_days_of_week(byte):
            days = []
            if byte & ReminderMasks.SUNDAY_MASK: days.append("SUNDAY")
            if byte & ReminderMasks.MONDAY_MASK: days.append("MONDAY")
            if byte & ReminderMasks.TUESDAY_MASK: days.append("TUESDAY")
            if byte & ReminderMasks.WEDNESDAY_MASK: days.append("WEDNESDAY")
            if byte & ReminderMasks.THURSDAY_MASK: days.append("THURSDAY")
            if byte & ReminderMasks.FRIDAY_MASK: days.append("FRIDAY")
            if byte & ReminderMasks.SATURDAY_MASK: days.append("SATURDAY")
            return days

        int_arr = to_int_array(data[2:])
        if int_arr[3] == 0xFF:
            EventsIO.result.set_result({"end": ""})
            return

        reminder = int_arr[2:]
        enabled, repeat = decode_time_period(reminder[0])
        start_date = decode_date(reminder[1:4])
        end_date = decode_date(reminder[4:7])
        days = decode_days_of_week(reminder[7])

        reminder_json = {
            "enabled": enabled,
            "repeat_period": repeat,
            "start_date": start_date,
            "end_date": end_date,
            "days_of_week": days
        }

        EventsIO.result.set_result(reminder_json)

class ReminderDecoder:
    def reminder_title_to_json(title_byte):
        hex_str = to_hex_string(title_byte)
        int_arr = to_int_array(hex_str)
        if int_arr[2] == 0xFF:
            return {"end": ""}
        return {"title": clean_str(to_ascii_string(hex_str, 2))}
