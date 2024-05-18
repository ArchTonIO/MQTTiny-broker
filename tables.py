""" properties for each packet of the mqtt 5.0 protocol. """
CONNECT_PROPERTIES_TABLE = {
    0x11: {
        "name": "session expiry interval",
        "type": "four_bytes_integer"
    },
    0x21: {
        "name": "receive maximum",
        "type": "two_bytes_integer"
    },
    0x27: {
        "name": "maximum packet size",
        "type": "four_bytes_integer"
    },
    0x22: {
        "name": "topic alias maximum",
        "type": "two_bytes_integer"
    },
    0x19: {
        "name": "request response information",
        "type": "byte"
    },
    0x17: {
        "name": "request problem information",
        "type": "byte"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    },
    0x15: {
        "name": "authentication method",
        "type": "utf-8_encoded_string"
    },
    0x16: {
        "name": "authentication data",
        "type": "binary_data"
    }
}

CONNACK_PROPERTIES_TABLE = {
    0x11: {
        "name": "session expiry interval",
        "type": "four_bytes_integer"
    },
    0x21: {
        "name": "receive maximum",
        "type": "two_bytes_integer"
    },
    0x24: {
        "name": "maximum qos",
        "type": "byte"
    },
    0x25: {
        "name": "retain available",
        "type": "bytes"
    },
    0x27: {
        "name": "maximum packet size",
        "type": "four_bytes_integer"
    },
    0x12: {
        "name": "assigned client identifier",
        "type": "utf-8_encoded_string"
    },
    0x22: {
        "name": "topic alias maximum",
        "type": "two_bytes_integer"
    },
    0x1f: {
        "name": "reason string",
        "type": "utf-8_encoded_string"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    },
    0x28: {
        "name": "wildcard subscription available",
        "type": "byte"
    },
    0x29: {
        "name": "subscription identifier available",
        "type": "bytes"
    },
    0x2a: {
        "name": "shared subscription available",
        "type": "byte"
    },
    0x13: {
        "name": "server keep alive",
        "type": "two_bytes_integer"
    },
    0x1a: {
        "name": "response information",
        "type": "utf-8_encoded_string"
    },
    0x1c: {
        "name": "server reference",
        "type": "utf-8_encoded_string"
    },
    0x15: {
        "name": "authentication method",
        "type": "utf-8_encoded_string"
    },
    0x16: {
        "name": "authentication data",
        "type": "binary_data"
    }
}

CONNACK_REASON_CODES = {
    0x00: "success",
    0x81: "malformed packet",
    0x82: "protocol error",
    0x84: "unsupported protocol version",
    0x85: "client identifier not valid",
    0x86: "bad user name or password",
    0x95: "packet too large",
    0x8a: "banned"
}

PUBLISH_PROPERTIES_TABLE = {
    0x01: {
        "name": "payload format indicator",
        "type": "byte"
    },
    0x02: {
        "name": "message expiry interval",
        "type": "four_bytes_integer"
    },
    0x23: {
        "name": "topic alias",
        "type": "two_bytes_integer"
    },
    0x08: {
        "name": "response topic",
        "type": "utf-8_encoded_string"
    },
    0x09: {
        "name":"correlation data",
        "type": "binary_data"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    },
    0x0b: {
        "name": "subscription identifier",
        "type": "variable byte integer"
    },
    0x03: {
        "name": "content type",
        "type": "utf-8_encoded_string"
    }
}

PUBACK_PROPERTIES_TABLE = {
    0x1f: {
        "name": "reason string",
        "type": "utf-8_encoded_string"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    }
}

PUBACK_REASON_CODES = {
    0x00: "success",
    0x10: "no matching subscribers",
    0x80: "unspecified error",
    0x83: "implementation specific error",
    0x87: "not authorized",
    0x90: "topic name invalid",
    0x91: "packet identifier in use",
    0x97: "quota exceeded",
    0x99: "payload format invalid"
}

PUBREC_PROPERTIES_TABLE = PUBACK_PROPERTIES_TABLE
PUBREL_PROPERTIES_TABLE = PUBACK_PROPERTIES_TABLE
PUBCOMP_PROPERTIES_TABLE = PUBACK_PROPERTIES_TABLE

PUBREL_REASON_CODES = {
    0x00: "success",
    0x92: "packet identifier not found"
}

PUBCOMP_REASON_CODES = PUBREL_REASON_CODES

SUBSCRIBE_PROPERTIES_TABLE = {
    0x0b: {
        "name": "subscription identifier",
        "type": "variable_byte_integer"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    }
}

SUBACK_PROPERTIES_TABLE = {
    0x1f: {
        "name": "reason string",
        "type": "utf-8_encoded_string"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    }
}

SUBACK_REASON_CODES = {
    0x00: "granted qos 0",
    0x01: "granted qos 1",
    0x02: "granted qos 2",
    0x80: "unspecified error",
    0x83: "implementation specific error",
    0x87: "not authorized",
    0x8f: "topic filter invalid",
    0x91: "packet identifier in use",
    0x97: "quota exceeded",
    0x9e: "shared subscriptions not supported",
    0xa1: "subscription identifiers not supported",
    0xa2: "wildcard subscriptions not supported"
}

UNSUBACK_REASON_CODES = {
    0x00: "success",
    0x11: "no subscription existed",
    0x80: "unspecified error",
    0x83: "implementation specific error",
    0x87: "not authorized",
    0x8f: "topic filter invalid",
    0x91: "packet identifier in use"
}

DISCONNECT_PROPERTIES_TABLE = {
    0x11: {
        "name": "session expiry interval",
        "type": "four_bytes_integer"
    },
    0x1f: {
        "name": "reason string",
        "type": "utf-8_encoded_string"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    },
    0x1c: {
        "name": "server reference",
        "type": "utf-8_encoded_string"
    }
}

DISCONNECT_REASON_CODES = {
    0x00: "normal disconnection",
    0x04: "disconnect with will message",
    0x81: "malformed packet",
    0x82: "protocol error",
    0x8d: "keep alive timeout",
    0x8e: "session taken over",
    0x93: "receive maximum exceeded",
    0x94: "topic alias invalid",
    0x95: "packet too large",
    0x98: "administrative action",
    0x9c: "use another server",
    0x9d: "server moved"
}

AUTH_PROPERTIES_TABLE = {
    0x15: {
        "name": "authentication method",
        "type": "utf-8_encoded_string"
    },
    0x16: {
        "name": "authentication data",
        "type": "binary_data"
    },
    0x1f: {
        "name": "reason string",
        "type": "utf-8_encoded_string"
    },
    0x26: {
        "name": "user property",
        "type": "utf-8_string_pair"
    }
}

AUTH_REASON_CODES = {
    0x00: "success",
    0x18: "continue authentication",
    0x19: "re-authenticate",
}
