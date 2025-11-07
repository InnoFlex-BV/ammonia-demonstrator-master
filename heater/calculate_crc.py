def calc_crc(data: bytes) -> bytes:
    """
    Calculate Modbus RTU CRC16 checksum.
    :param data: bytes or bytearray to compute CRC on
    :return: 2-byte CRC (little-endian)
    """
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')
