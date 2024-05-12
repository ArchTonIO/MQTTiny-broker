""" This module contains the classes to handle the MQTT 5.0 packets. """
PUBLISH_PROPERTIES_TABLE = {
    1: {
        "name": "Payload Format Indicator",
        "type": "byte",
    },
    2: {
        "name": "Message Expiry Interval",
        "type": "four_bytes_integer",
    },
    3: {
        "name": "Content Type",
        "type": "utf-8_encoded_string",
    },
    8: {
        "name": "Response Topic",
        "type": "utf-8_encoded_string",
    },
    9: {
        "name":"Correlation Data",
        "type": "binary_data",
    },
    11: {
        "name": "Subscription Identifier",
        "type": "variable_byte_integer",
    },
    35: {
        "name": "Topic Alias",
        "type": "two_bytes_integer",
    },
    38: {
        "name": "User Property",
        "type": "utf-8_string_pair",
    }
}


def decode_variable_length_integer(_bytes: bytes) -> tuple:
    """
    Decode a variable length integer.

    Returns
    -------
    tuple : the value of the integer and the number of bytes used to encode it.
    """
    multiplier = 1
    value = 0
    byte_index = 0
    while True:
        byte = _bytes[byte_index]
        value += (byte & 127) * multiplier
        multiplier *= 128
        byte_index += 1
        if (byte & 128) == 0:
            break
    return value, byte_index


class Publish:
    """
    Class to handle the PUBLISH MQTT 5.0 packet.

    Attributes
    ----------
    raw : bytes, the raw bytes message.
    bits : list, the bits of the raw message.
    fixed_header : bytes, the fixed header of the message.
    retain : int, the retain flag of the message.
    qos : int, the qos of the message.
    dup : int, the dup flag of the message.
    packet_type : hex, the packet type of the message.
    topic : bytes, the topic of the message.
    properties_length : int, the length of the properties.
    properties : dict, the properties of the message.
    payload : bytes, the payload of the message.
    """
    def __init__(self, bytes_message: bytes) -> None:
        self.raw = bytes_message
        self.remaining_length_ecoding_bytes = 2 if len(self.raw) > 129 else 1
        self.bits = [f"{byte:b}" for byte in bytes_message]
        self.bits = [
            "0" * (8 - len(bit)) + bit 
            if len(bit) < 8 else bit for bit in self.bits
        ]
        self.fixed_header = None
        self.retain = None
        self.qos = None
        self.dup = None
        self.packet_type = None
        self.topic = None
        self.properties_length = None
        self.properties = {}
        self.payload = None
        self._unpack_fixed_header()
        self._unpack_variable_header()

    def _unpack_fixed_header(self) -> None:
        """ Unpack the fixed header of the message. """
        fixed_header = self.bits[0]
        self.fixed_header = fixed_header.encode()
        self.retain = int(fixed_header[-1], 2)
        self.qos = int(fixed_header[-3:-1], 2)
        self.dup = int(fixed_header[-4], 2)
        self.packet_type = hex(fixed_header[-7:-4].encode()[0])

    def _unpack_variable_header(self) -> None:
        """ Unpack the variable header and the payload of the message. """
        self.remaining_length, self._cursor = decode_variable_length_integer(
            self.raw[1:]
        )
        self._cursor += 1
        self.topic_length = int(self.bits[self._cursor], 2) + int(
            self.bits[self._cursor + 1], 2
        )
        self._cursor += 2
        self.topic = self.raw[self._cursor:self._cursor + self.topic_length]
        self._cursor += self.topic_length
        self._unpack_properties()
        self.payload = self.raw[self._cursor: self.remaining_length + 2]

    def _unpack_properties(self) -> None:
        """ Unpack the properties of the message. """
        read_bytes = 0
        self.properties_length, positions = decode_variable_length_integer(
            self.raw[self._cursor:]
        )
        self._cursor += positions
        _cursor = self._cursor
        self._cursor += self.properties_length
        while read_bytes < self.properties_length:
            _property = self.raw[_cursor]
            read_bytes += 1
            _cursor += 1
            property_name = PUBLISH_PROPERTIES_TABLE[_property]["name"]
            value = None
            lenght = 0
            if PUBLISH_PROPERTIES_TABLE[_property]["type"] == "byte":
                value = self.raw[_cursor]
                lenght = 1
            elif (
                PUBLISH_PROPERTIES_TABLE[_property]["type"]
                == "four_bytes_integer"
            ):
                value = int.from_bytes(self.raw[_cursor:_cursor + 4], "big")
                lenght = 4
                _cursor += 4
            elif (
                (
                    PUBLISH_PROPERTIES_TABLE[_property]["type"]
                    == "utf-8_encoded_string"
                )
            ):
                _lenght = 2
                _str_len = int.from_bytes(self.raw[_cursor:_cursor + _lenght],
                "big"
                )
                _cursor += _lenght
                value = self.raw[_cursor:_cursor + _str_len]
                lenght = _str_len + _lenght
                _cursor += _str_len
            elif (
                PUBLISH_PROPERTIES_TABLE[_property]["type"]
                == "variable_byte_integer"
            ):
                value, lenght = decode_variable_length_integer(
                    self.raw[_cursor:]
                )
                _cursor += lenght
            elif (
                PUBLISH_PROPERTIES_TABLE[_property]["type"]
                == "two_bytes_integer"
            ):
                value = int.from_bytes(self.raw[_cursor:_cursor + 2], "big")
                lenght = 2
                _cursor += 2
            self.properties[property_name] = PUBLISH_PROPERTIES_TABLE[
                _property
            ] = value
            read_bytes += lenght

    def __repr__(self) -> str:  # sourcery skip: use-fstring-for-concatenation
        return (
            "> PUBLISH MQTT 5.0 PACKET <\n"
            f"raw: {self.raw}\n"
            + f"fixed_header: {self.fixed_header}\n"
            + f"retain: {self.retain}\n"
            + f"qos: {self.qos}\n"
            + f"dup: {self.dup}\n"
            + f"packet_type: {self.packet_type}\n"
            + f"remaining_length: {self.remaining_length}\n"
            + f"topic_length: {self.topic_length}\n"
            + f"topic: {self.topic}\n"
            + f"properties_length: {self.properties_length}\n"
            + f"properties: {self.properties}\n"
            + f"payload: {self.payload}\n"
            + ''.join(
                [
                    f"BYTE_{n if n > 9 else '0' + str(n)}: {bit} --> \
                    {hex(self.raw[n])} --> \
                    {chr(self.raw[n])}\n" for n, bit in enumerate(self.bits)
                ]
            )
        )
