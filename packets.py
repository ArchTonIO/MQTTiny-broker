""" This module contains the classes to handle the MQTT 5.0 packets. """
from tables import CONNECT_PROPERTIES_TABLE, PUBLISH_PROPERTIES_TABLE


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


class Connect:
    """
    Class to handle the CONNECT MQTT 5.0 packet.

    Attributes
    ----------
    raw : bytes, the raw bytes message.
    bits : list, the bits of the raw message.
    fixed_header : bytes, the fixed header of the message.
    protocol_name : bytes, the protocol name of the message.
    protocol_version : int, the protocol version of the message.
    connect_flags : dict, the connect flags of the message.
    keep_alive : int, the keep alive of the message.
    properties_length : int, the length of the properties.
    client_id : bytes, the client id of the message.
    will_topic : bytes, the will topic of the message.
    will_payload : bytes, the will payload of the message.
    user_name : bytes, the user name of the message.
    password : bytes, the password of the message.
    properties : dict, the properties of the message.
    connect_flags : dict, the connect flags of the message.
    """
    def __init__(self, bytes_message: bytes) -> None:
        self.raw = bytes_message
        self.bits = [f"{byte:b}" for byte in bytes_message]
        self.bits = [
            "0" * (8 - len(bit)) + bit 
            if len(bit) < 8 else bit for bit in self.bits
        ]
        self.fixed_header = None
        self.protocol_name = None
        self.protocol_version = None
        self.connect_flags = None
        self.keep_alive = None
        self.properties_length = None
        self.client_id = None
        self.user_name = None
        self.password = None
        self.will_retain = None
        self.will_qos = None
        self.will_properties = None
        self.will_topic = None
        self.will_payload = None
        self.clean_start = None
        self.properties = {}
        self.connect_flags = {}
        self._cursor = 0
        self._unpack_fixed_header()
        self._unpack_variable_header()
        self._unpack_properties()
        self._unpack_payload()

    def _unpack_fixed_header(self) -> None:
        """ Unpack the fixed header of the message. """
        fixed_header = self.bits[0]
        self.fixed_header = fixed_header.encode()
        self._cursor += 1

    def _unpack_connection_flags(self) -> None:
        """ Unpack the connection flags of the message. """
        connect_flags = self.bits[self._cursor]
        self.connect_flags["username"] = bool(int(connect_flags[0], 2))
        self.connect_flags["password"] = bool(int(connect_flags[1], 2))
        self.connect_flags["will_retain"] = bool(int(connect_flags[2], 2))
        self.connect_flags["will_qos"] = int(connect_flags[3:4], 2)
        self.connect_flags["will_flag"] = bool(int(connect_flags[5], 2))
        self.connect_flags["clean_start"] = bool(int(connect_flags[6], 2))
        self.connect_flags["reserved"] = int(connect_flags[7], 2)
        self._cursor += 1

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
            _property = int(hex(self.raw[_cursor]), 16)
            read_bytes += 1
            _cursor += 1
            property_name = CONNECT_PROPERTIES_TABLE[_property]["name"]
            value = None
            lenght = 0
            if CONNECT_PROPERTIES_TABLE[_property]["type"] == "byte":
                value = self.raw[_cursor]
                lenght = 1
            elif (
                CONNECT_PROPERTIES_TABLE[_property]["type"]
                == "four_bytes_integer"
            ):
                value = int.from_bytes(self.raw[_cursor:_cursor + 4], "big")
                lenght = 4
                _cursor += 4
            elif (
                (
                    CONNECT_PROPERTIES_TABLE[_property]["type"]
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
                CONNECT_PROPERTIES_TABLE[_property]["type"]
                == "variable_byte_integer"
            ):
                value, lenght = decode_variable_length_integer(
                    self.raw[_cursor:]
                )
                _cursor += lenght
            elif (
                CONNECT_PROPERTIES_TABLE[_property]["type"]
                == "two_bytes_integer"
            ):
                value = int.from_bytes(self.raw[_cursor:_cursor + 2], "big")
                lenght = 2
                _cursor += 2
            self.properties[property_name] = CONNECT_PROPERTIES_TABLE[
                _property
            ] = value
            read_bytes += lenght

    def _unpack_payload(self) -> None:
        """ Unpack the payload of the message. """
        client_id_len = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        self.client_id = self.raw[
            self._cursor:self._cursor + client_id_len
        ]
        self._cursor += client_id_len
        if self.connect_flags["will_flag"]:
            self.will_properties = self.raw[self._cursor:self._cursor + 2]
            self._cursor += 2
            self.will_properties = self._unpack_payload_inner()
            self.will_topic = self.raw[self._cursor:self._cursor + 2]
            self._cursor += 2
            self.will_topic = self._unpack_payload_inner()
            self.will_payload = self.raw[self._cursor:self._cursor + 2]
            self._cursor += 2
            self.will_payload = self._unpack_payload_inner()
        if self.connect_flags["username"]:
            self.user_name = self._unpack_payload_inner()
        if self.connect_flags["password"]:
            self.password = self._unpack_payload_inner()

    def _unpack_payload_inner(self) -> bytes:
        """ Unpack the inner parts of the message payload. """
        payload_length = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        result = self.raw[self._cursor : self._cursor + payload_length]
        self._cursor += payload_length
        return result

    def _unpack_variable_header(self) -> None:
        """ Unpack the variable header of the message. """
        _, read_bytes = decode_variable_length_integer(
            self.raw[1:]
        )
        self._cursor += read_bytes
        protocol_name_length = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        self.protocol_name = self.raw[
            self._cursor:self._cursor + protocol_name_length
        ]
        if self.protocol_name != b"MQTT":
            raise ValueError("Invalid protocol name")
        self._cursor += 4
        self.protocol_version = self.raw[self._cursor]
        if self.protocol_version != 5:
            raise ValueError("Invalid protocol version")
        self._cursor += 1
        self._unpack_connection_flags()
        self.keep_alive = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2

    def __repr__(self) -> str:  # sourcery skip: use-fstring-for-concatenation
        return (
            "> CONNECT MQTT 5.0 PACKET <\n"
            f"raw: {self.raw}\n"
            + f"fixed_header: {self.fixed_header}\n"
            + f"protocol_name: {self.protocol_name}\n"
            + f"protocol_version: {self.protocol_version}\n"
            + f"connect_flags: {self.connect_flags}\n"
            + f"keep_alive: {self.keep_alive}\n"
            + f"properties_length: {self.properties_length}\n"
            + f"client_id: {self.client_id}\n"
            + f"will_topic: {self.will_topic}\n"
            + f"will_payload: {self.will_payload}\n"
            + f"user_name: {self.user_name}\n"
            + f"password: {self.password}\n"
            + f"properties: {self.properties}\n"
            + ''.join(
                [
                    f"BYTE_{n if n > 9 else '0' + str(n)}: {bit} --> \
                    {hex(self.raw[n])} --> \
                    {chr(self.raw[n])}\n" for n, bit in enumerate(self.bits)
                ]
            )
        )


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
            _property = int(hex(self.raw[_cursor]), 16)
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
