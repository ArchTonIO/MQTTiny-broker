""" This module contains the classes to handle the MQTT 5.0 packets. """
from MQTT5.exceptions import (
    BadAuthenticationMethodException,
    BadUserNameOrPasswordException,
    BannedException,
    ClientIdNotValidException,
    ConnectionRateExceededException,
    MalformedPacketException,
    NotAuthorizedException,
    PacketTooLargeException,
    PayloadFormatException,
    ProtocolErrorException,
    QosNotSupportedException,
    QuotaExceededException,
    ReceiveMaximumExceededException,
    RetainNotSupportedException,
    ServerBusyException,
    ServerMovedException,
    ServerUnavailableException,
    SharedSubscriptionNotSupportedException,
    SubscriptionIdentifierNotSupportedException,
    TopicNameInvalidException,
    UnsupportedProtocolVersionException,
    UseAnotherServerException,
    WildcardSubscriptionNotSupportedException,
)
from MQTT5.tables import (
    CONNACK_PROPERTIES_TABLE,
    CONNACK_REASON_CODES,
    CONNECT_PROPERTIES_TABLE,
    PUBLISH_PROPERTIES_TABLE,
    SUBSCRIBE_PROPERTIES_TABLE
)


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


class ConnectUnpacker:
    """
    Unpack a CONNECT MQTT 5.0 packet received from a client.

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

    def unpack(self) -> None:
        """ Unpack the message. """
        self._unpack_fixed_header()
        self._unpack_variable_header()
        self._unpack_payload()
        self._ceck_errors()

    def _unpack_fixed_header(self) -> None:
        """ Unpack the message fixed header. """
        fixed_header = self.bits[0]
        self.fixed_header = fixed_header.encode()
        self._cursor += 1

    def _unpack_variable_header(self) -> None:
        """ Unpack the message variable header."""
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
        self._cursor += 4
        self.protocol_version = self.raw[self._cursor]
        self._cursor += 1
        self._unpack_connection_flags()
        self.keep_alive = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        self._unpack_properties()

    def _unpack_properties(self) -> None:
        """ Unpack the message properties."""
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
            self.properties[property_name] = value
            read_bytes += lenght

    def _unpack_payload(self) -> None:
        """ Unpack the message payload. """
        client_id_len = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        self.client_id = self.raw[
            self._cursor:self._cursor + client_id_len
        ]
        self._cursor += client_id_len
        if self.connect_flags["will_flag"]:
            self.will_properties = self._unpack_will_flags()
            self.will_topic = self._unpack_will_flags()
            self.will_payload = self._unpack_will_flags()
        if self.connect_flags["username"]:
            self.user_name = self._unpack_payload_inner()
        if self.connect_flags["password"]:
            self.password = self._unpack_payload_inner()

    def _unpack_connection_flags(self) -> None:
        """ Unpack the message connection flags."""
        connect_flags = self.bits[self._cursor]
        self.connect_flags["username"] = bool(int(connect_flags[0], 2))
        self.connect_flags["password"] = bool(int(connect_flags[1], 2))
        self.connect_flags["will_retain"] = bool(int(connect_flags[2], 2))
        self.connect_flags["will_qos"] = int(connect_flags[3:4], 2)
        self.connect_flags["will_flag"] = bool(int(connect_flags[5], 2))
        self.connect_flags["clean_start"] = bool(int(connect_flags[6], 2))
        self.connect_flags["reserved"] = int(connect_flags[7], 2)
        self._cursor += 1

    def _unpack_will_flags(self):
        """ Unpack message will flags. """
        self._cursor += 2
        return self._unpack_payload_inner()

    def _unpack_payload_inner(self) -> bytes:
        """ Unpack the message payload inner parts. """
        payload_length = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        result = self.raw[self._cursor : self._cursor + payload_length]
        self._cursor += payload_length
        return result

    def _ceck_errors(self) -> None:
        """ Check for errors in the message. """
        if self.connect_flags["will_qos"] != 0:
            raise QosNotSupportedException("Qos not supported")
        if self.connect_flags["will_retain"]:
            raise RetainNotSupportedException("Retain not supported")
        if self.protocol_name != b"MQTT":
            raise ProtocolErrorException("Invalid protocol name")
        if self.protocol_version != 5:
            raise UnsupportedProtocolVersionException(
                "Invalid protocol version"
            )

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


class PublishUnpacker:
    """
    Unpack a PUBLISH MQTT 5.0 packet received from a client.

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
        self._cursor = 0
        self.remaining_length = 0
        self.topic_length = 0

    def unpack(self) -> None:
        """ Unpack the message. """
        self._unpack_fixed_header()
        self._unpack_variable_header()
        self._unpack_payload()

    def _unpack_fixed_header(self) -> None:
        """ Unpack  message fixed header. """
        fixed_header = self.bits[0]
        self.fixed_header = fixed_header.encode()
        self.retain = int(fixed_header[-1], 2)
        self.qos = int(fixed_header[-3:-1], 2)
        self.dup = int(fixed_header[-4], 2)
        self.packet_type = hex(fixed_header[-7:-4].encode()[0])

    def _unpack_variable_header(self) -> None:
        """ Unpack the message variable header. """
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

    def _unpack_properties(self) -> None:
        """ Unpack the message properties. """
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
            self.properties[property_name] = value
            read_bytes += lenght

    def _unpack_payload(self) -> None:
        """ Unpack the message payload. """
        self.payload = self.raw[self._cursor: self.remaining_length + 2]

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


class ConnackPacker:
    """
    Pack up a CONNACK MQTT 5.0 package to be sent to the client.
    """
    def __init__(
        self,
        session_present: bool,
        reason_code: str,
        properties: dict = None
    ) -> None:
        self.raw = bytearray()
        self.bits = None
        self.session_present = session_present
        self.reason_code = reason_code
        self.properties = properties or {
            "maximum qos": b"\x00",
            "retain available": b"\x00",
            "maximum packet size": b"\x00\x10\x00\x00",
            "wildcard subscription available": b"\x00",
            # "server keep alive": b"\x3c\x00"
        }

    def pack(self) -> bytes:
        """ Pack the message. """
        self._pack_fixed_header()
        self._pack_variable_header()
        self._calculate_bits()
        self.raw = bytes(self.raw)
        return self.raw

    def _pack_fixed_header(self) -> None:
        """ Pack the message fixed header. """
        self.raw.append(0x20)
        self.raw.append(0x00)

    def _pack_variable_header(self) -> None:
        """ Pack the message variable header. """
        self.raw.append(0x00)
        if self.session_present:
            self.raw[2] = 0x01
        self.raw.append(CONNACK_REASON_CODES[self.reason_code])
        self._pack_properties()
        self._calculate_remaining_length()

    def _pack_properties(self) -> None:
        """ Pack the message properties. """
        properties_array = bytearray()
        for k, v in self.properties.items():
            properties_array.append(CONNACK_PROPERTIES_TABLE[k])
            properties_array.extend(v)
        properties_length = len(properties_array)
        self.raw.append(properties_length)
        self.raw.extend(properties_array)

    def _calculate_remaining_length(self) -> None:
        """ Calculate the remaining length of the message. """
        self.raw[1] = len(self.raw) - 2

    def _calculate_bits(self) -> None:
        self.bits = [f"{byte:b}" for byte in self.raw]
        self.bits = [
            "0" * (8 - len(bit)) + bit 
            if len(bit) < 8 else bit for bit in self.bits
        ]

    def __repr__(self) -> str: # sourcery skip: use-fstring-for-concatenation
        return (
            "> CONNACK MQTT 5.0 PACKET <\n"
            + f"Raw: {self.raw}\n"
            + f"Session present: {self.session_present}\n"
            + f"Reason code: {self.reason_code}\n"
            + f"Properties: {self.properties}\n"
            + ''.join(
                [
                    f"BYTE_{n if n > 9 else '0' + str(n)}: {bit} --> \
                    {hex(self.raw[n])} --> \
                    {chr(self.raw[n])}\n" for n, bit in enumerate(self.bits)
                ]
            )
        )


class SubscribeUnpacker:
    """ Unpack a SUBSCRIBE MQTT 5.0 packet received from a client. """
    def __init__(self, bytes_message: str) -> None:
        self.raw = bytes_message
        self.bits = [f"{byte:b}" for byte in bytes_message]
        self.bits = [
            "0" * (8 - len(bit)) + bit 
            if len(bit) < 8 else bit for bit in self.bits
        ]
        self._cursor = 0
        self.fixed_header = None
        self.remaining_length = 0
        self.packet_identifier = 0
        self.properties_length = 0
        self.properties = {}
        self.topic = 0
        self.maximum_qos = 0
        self.no_local = 0
        self.retain_as_published = 0
        self.retain_handling = 0

    def unpack(self) -> None:
        """ Unpack the message. """
        self._unpack_fixed_header()
        self._unpack_variable_header()
        self._unpack_payload()

    def _unpack_fixed_header(self) -> None:
        """ Unpack the message fixed header. """
        self.fixed_header = self.bits[0]
        if self.fixed_header[4:] != "0010":
            raise MalformedPacketException("Malformed packet")
        self.remaining_length, self._cursor = decode_variable_length_integer(
            self.raw[1:]
        )
        self._cursor += 1

    def _unpack_variable_header(self) -> None:
        """ Unpack the message variable header. """
        self.packet_identifier = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        self._unpack_properties()

    def _unpack_properties(self) -> None:
        """ Unpack the message properties. """
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
            property_name = SUBSCRIBE_PROPERTIES_TABLE[_property]["name"]
            value = None
            lenght = 0
            if SUBSCRIBE_PROPERTIES_TABLE[_property]["type"] == "byte":
                value = self.raw[_cursor]
                lenght = 1
            elif (
                SUBSCRIBE_PROPERTIES_TABLE[_property]["type"]
                == "four_bytes_integer"
            ):
                value = int.from_bytes(self.raw[_cursor:_cursor + 4], "big")
                lenght = 4
                _cursor += 4
            elif (
                (
                    SUBSCRIBE_PROPERTIES_TABLE[_property]["type"]
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
                SUBSCRIBE_PROPERTIES_TABLE[_property]["type"]
                == "variable_byte_integer"
            ):
                value, lenght = decode_variable_length_integer(
                    self.raw[_cursor:]
                )
                _cursor += lenght
            elif (
                SUBSCRIBE_PROPERTIES_TABLE[_property]["type"]
                == "two_bytes_integer"
            ):
                value = int.from_bytes(self.raw[_cursor:_cursor + 2], "big")
                lenght = 2
                _cursor += 2
            self.properties[property_name] = value
            read_bytes += lenght

    def _unpack_payload(self) -> None:
        if self._cursor == self.remaining_length:
            raise ProtocolErrorException("Protocol error: no payload")
        topic_length = int.from_bytes(
            self.raw[self._cursor:self._cursor + 2], "big"
        )
        self._cursor += 2
        self.topic = self.raw[
            self._cursor:self._cursor + topic_length
        ]
        self._cursor += topic_length
        subscription_options = self.bits[self._cursor]
        self.maximum_qos = int(
            subscription_options[-2] + subscription_options[-1], 2
        )
        # if self.maximum_qos > 0:
        #     raise QosNotSupportedException("Qos not supported")
        if self.maximum_qos > 2:
            raise ProtocolErrorException("Protocol error: invalid qos 3")
        self.no_local = int(subscription_options[-3], 2)
        self.retain_as_published = int(subscription_options[-4], 2)
        self.retain_handling = int(subscription_options[-5], 2)

def __repr__(self) -> str:  # sourcery skip: use-fstring-for-concatenation
    return (
        "> SUBSCRIBE MQTT 5.0 PACKET <\n"
        f"raw: {self.raw}\n"
        + f"fixed_header: {self.fixed_header}\n"
        + f"remaining_length: {self.remaining_length}\n"
        + f"packet_identifier: {self.packet_identifier}\n"
        + f"properties_length: {self.properties_length}\n"
        + f"properties: {self.properties}\n"
        + f"topic: {self.topic}\n"
        + f"maximum_qos: {self.maximum_qos}\n"
        + f"no_local: {self.no_local}\n"
        + f"retain_as_published: {self.retain_as_published}\n"
        + f"retain_handling: {self.retain_handling}\n"
        + ''.join(
            [
                f"BYTE_{n if n > 9 else '0' + str(n)}: {bit} --> \
                {hex(self.raw[n])} --> \
                {chr(self.raw[n])}\n" for n, bit in enumerate(self.bits)
            ]
        )
)


def handle_mqtt5_protocol_errors(func: callable) -> callable:
    """decorator to handle MQTT 5.0 protocol errors."""

    def wrapper(*args, **kwargs) -> callable:
        sock = args[1]
        try:
            return func(*args, **kwargs)
        except MalformedPacketException:
            print(
                "Closing connection with client due to: Malformed packet"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="malformed packet"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ProtocolErrorException:
            print("Closing connection with client due to: Protocol error")
            connack = ConnackPacker(
                session_present=False,
                reason_code="protocol error"
            )
            sock.sendall(connack.pack())
            sock.close()
        except UnsupportedProtocolVersionException:
            print(
                "Closing connection with client due to: "
                "Unsupported protocol version"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="unsupported protocol version"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ClientIdNotValidException:
            print(
                "Closing connection with client due to: "
                "Client id not valid"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="client identifier not valid"
            )
            sock.sendall(connack.pack())
            sock.close()
        except BadUserNameOrPasswordException:
            print(
                "Closing connection with client due to: Bad "
                "username or password"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="bad user name or password"
            )
            sock.sendall(connack.pack())
            sock.close()
        except NotAuthorizedException:
            print("Closing connection with client due to: Not authorized")
            connack = ConnackPacker(
                session_present=False,
                reason_code="not authorized"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ServerUnavailableException:
            print(
                "Closing connection with client due to: Server unavailable"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="server unavailable"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ServerBusyException:
            print("Closing connection with client due to: Server busy")
            connack = ConnackPacker(
                session_present=False,
                reason_code="server busy"
            )
            sock.sendall(connack.pack())
            sock.close()
        except BannedException:
            print("Closing connection with client due to: Banned")
            connack = ConnackPacker(
                session_present=False,
                reason_code="banned"
            )
            sock.sendall(connack.pack())
            sock.close()
        except BadAuthenticationMethodException:
            print(
                "Closing connection with client due to: Bad "
                "authentication method"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="authentication method invalid"
            )
            sock.sendall(connack.pack())
            sock.close()
        except TopicNameInvalidException:
            print(
                "Closing connection with client due to: Topic name invalid"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="topic name invalid"
            )
            sock.sendall(connack.pack())
            sock.close()
        except PacketTooLargeException:
            print(
                "Closing connection with client due to: Packet too large"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="packet too large"
            )
            sock.sendall(connack.pack())
            sock.close()
        except QuotaExceededException:
            print("Closing connection with client due to: Quota exceeded")
            connack = ConnackPacker(
                session_present=False,
                reason_code="quota exceeded"
            )
            sock.sendall(connack.pack())
            sock.close()
        except PayloadFormatException:
            print(
                "Closing connection with client due to: Payload "
                "format invalid"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="payload format invalid"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ReceiveMaximumExceededException:
            print(
                "Closing connection with client due to: "
                "Receive maximum exceeded"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="receive maximum exceeded"
            )
            sock.sendall(connack.pack())
            sock.close()
        except QosNotSupportedException:
            print(
                "Closing connection with client due to: QoS not supported"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="qos not supported"
            )
            sock.sendall(connack.pack())
            sock.close()
        except RetainNotSupportedException:
            print(
                "Closing connection with client due to: Retain not "
                "supported"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="retain not supported"
            )
            sock.sendall(connack.pack())
            sock.close()
        except SharedSubscriptionNotSupportedException:
            print(
                "Closing connection with client due to: "
                "Shared subscription not supported"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="shared subscription not supported"
            )
            sock.sendall(connack.pack())
            sock.close()
        except UseAnotherServerException:
            print(
                "Closing connection with client due to: Use another server"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="use another server"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ServerMovedException:
            print("Closing connection with client due to: Server moved")
            connack = ConnackPacker(
                session_present=False,
                reason_code="server moved"
            )
            sock.sendall(connack.pack())
            sock.close()
        except ConnectionRateExceededException:
            print(
                "Closing connection with client due to: "
                "Connection rate exceeded"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="connection rate exceeded"
            )
            sock.sendall(connack.pack())
            sock.close()
        except SubscriptionIdentifierNotSupportedException:
            print(
                "Closing connection with client due to: "
                "subscription identifier not supported"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="subscription identifier not supported"
            )
            sock.sendall(connack.pack())
            sock.close()
        except WildcardSubscriptionNotSupportedException:
            print(
                "Closing connection with client due to: "
                "Wildcard subscription not supported"
            )
            connack = ConnackPacker(
                session_present=False,
                reason_code="wildcard subscription not supported"
            )
            sock.sendall(connack.pack())
            sock.close()
    return wrapper
