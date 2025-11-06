import uasyncio as asyncio
import json

class LogSender:

    async def send_logs(self, connection, activity_log):
        log_data = activity_log.to_json()  # Get JSON string
        self.print_dates(log_data)

        log_bytes = log_data.encode('utf-8') 
        
        length_bytes = len(log_bytes).to_bytes(4, 'big')
        await connection.write_logs(0xAA, length_bytes)
        
        # Send subsequent chunks of max 17 bytes
        start = 0
        chunk_size = 17
        while start < len(log_bytes):
            chunk = log_bytes[start:start+chunk_size]
            await connection.write_logs(0xAA, chunk)
            start += chunk_size

    def print_dates(self, log_data):
        # Parse the JSON string into a Python list of dictionaries
        log_list = json.loads(log_data)

        # Iterate through each log entry in the list
        for entry in log_list:
            # Access and print the "datetime" field


log_sender = LogSender()