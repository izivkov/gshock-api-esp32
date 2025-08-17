import utime as time  # MicroPython's time module

def to_casio_cmd(bytes_str):
    parts = [bytes_str[i:i+2] for i in range(0, len(bytes_str), 2)]
    return bytes(int(p, 16) for p in parts)

def to_int_array(hex_str):
    int_arr = []
    for s in hex_str.split(" "):
        if s.startswith("0x"):
            s = s[2:]
        int_arr.append(int(s, 16))
    return int_arr

def to_compact_string(hex_str):
    parts = []
    for s in hex_str.split(" "):
        if s.startswith("0x"):
            s = s[2:]
        parts.append(s)
    return "".join(parts)

def to_hex_string(byte_arr):
    return "0x" + " ".join("%02X" % x for x in byte_arr)

def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

def to_ascii_string(hex_str, command_length_to_skip):
    if " " in hex_str:
        str_array = hex_str.split(" ")
    else:  # No spaces, raw hex
        str_array = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    str_array = str_array[command_length_to_skip:]
    return bytes.fromhex("".join(str_array)).decode("ASCII")

def trim_non_ascii_characters(s):
    return s.replace("\0", "")

def current_milli_time():
    return round(time.time() * 1000)

def clean_str(dirty_str):
    # Keep only printable ASCII (0x20–0x7E)
    return "".join(c for c in dirty_str if 32 <= ord(c) <= 126)

def to_byte_array(s, max_len):
    b = s.encode("utf-8")
    if len(b) > max_len:
        return b[:max_len]
    elif len(b) < max_len:
        return b + bytearray(max_len - len(b))
    return b

def to_hex_string_compact(ascii_str, max_len):
    b = bytearray(ascii_str, 'ascii')
    return "".join("{:02x}".format(byte) for byte in b[:max_len])

def dec_to_hex(dec):
    return int(str(hex(dec))[2:])

def encode_string(ascii_string, maxlen):
    int_arr = [ord(c) for c in ascii_string]
    while len(int_arr) < maxlen:
        int_arr.append(0)
    return "".join("{:02X}".format(i) for i in int_arr)
