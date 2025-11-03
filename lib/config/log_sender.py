import uasyncio as asyncio

class LogSender:
    async def send_logs(self, connection, activity_log):
        log_data = activity_log.to_json()  # Get JSON string
        log_bytes = log_data.encode('utf-8')    # Encode to bytes
        
        length_bytes = len(log_bytes).to_bytes(4, 'big')
        # Send first chunk: 4 bytes with length of log data
        await connection.write_logs(0xAA, length_bytes)
        
        # Send subsequent chunks of max 17 bytes
        start = 0
        chunk_size = 17
        while start < len(log_bytes):
            chunk = log_bytes[start:start+chunk_size]
            await connection.write_logs(0xAA, chunk)
            start += chunk_size

log_sender = LogSender()