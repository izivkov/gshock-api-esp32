import time

def to_casio_cmd(bytesStr):
    parts = [bytesStr[i:i + 2] for i in range(0, len(bytesStr), 2)]
    hexArr = [int(s, 16) for s in parts]
    return bytes(hexArr)


def to_int_array(hexStr):
    intArr = []
    strArray = hexStr.split(" ")
    for s in strArray:
        if s.startswith("0x"):
            s = s[2:]
        intArr.append(int(s, 16))
    return intArr


def to_compact_string(hexStr):
    compactString = ""
    strArray = hexStr.split(" ")
    for s in strArray:
        if s.startswith("0x"):
            s = remove_prefix(s, "0x")
        compactString += s
    return compactString


def to_hex_string(byte_arr):
    return "0x" + " ".join("{:02X}".format(x) for x in byte_arr)


def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s


def to_ascii_string(hexStr, commandLengthToSkip):
    strArray = hexStr.split(" ")
    if len(strArray) == 1:
        strArray = [hexStr[i:i + 2] for i in range(0, len(hexStr), 2)]

    strArray = strArray[commandLengthToSkip:]
    asc = "".join(strArray)
    return bytes.fromhex(asc).decode("ASCII")


def trim_non_ascii_characters(s):
    return s.replace("\0", "")


def current_milli_time():
    return round(time.time() * 1000)


def clean_str(dirty_str):
    # MicroPython doesn't have string.printable; use simple ASCII range check
    return "".join(c for c in dirty_str if 32 <= ord(c) <= 126)


def to_byte_array(s, maxLen):
    retArr = s.encode("utf-8")
    if len(retArr) > maxLen:
        return retArr[:maxLen]
    elif len(retArr) < maxLen:
        return retArr + bytearray(maxLen - len(retArr))
    else:
        return retArr


def to_hex_string_compact(asciiStr, maxLen):
    byteArr = bytearray(asciiStr, 'ascii')
    hexStr = ""
    for byte in byteArr[:maxLen]:
        hexStr += "{:02x}".format(byte)
    return hexStr


def dec_to_hex(dec):
    return int("{:X}".format(dec), 16)


def encode_string(ascii_string, maxlen):
    int_arr = [ord(c) for c in ascii_string]
    while len(int_arr) < maxlen:
        int_arr.append(0)
    hex_string = ''
    for i in int_arr:
        hex_string += '{:02X}'.format(i)
    return hex_string
