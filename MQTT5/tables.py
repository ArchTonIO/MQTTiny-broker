""" Tables for each packet of the MQTT 5.0 protocol. """
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
    "session expiry interval": 0x11,
    "receive maximum": 0x21,
    "maximum qos": 0x24,
    "retain available": 0x25,
    "maximum packet size": 0x27,
    "assigned client identifier": 0x12,
    "topic alias maximum": 0x22,
    "reason string": 0x1f,
    "user property": 0x26,
    "wildcard subscription available": 0x28,
    "subscription identifier available": 0x29,
    "shared subscription available": 0x2a,
    "server keep alive": 0x13,
    "response information": 0x1a,
    "server reference": 0x1c,
    "authentication method": 0x15,
    "authentication data": 0x16
}

CONNACK_REASON_CODES = {
    "success": 0x00,
    "unspecified error": 0x80,
    "malformed packet": 0x81,
    "protocol error": 0x82,
    "implementation specific error": 0x83,
    "unsupported protocol version": 0x84,
    "client identifier not valid": 0x85,
    "bad user name or password": 0x86,
    "not authorized": 0x87,
    "server unavailable": 0x88,
    "server busy": 0x89,
    "banned": 0x8a,
    "bad authentication method": 0x8c,
    "topic name invalid": 0x90,
    "packet too large": 0x95,
    "quota exceeded": 0x97,
    "payload format invalid": 0x99,
    "retain not supported": 0x9a,
    "qos not supported": 0x9b,
    "use another server": 0x9c,
    "server moved": 0x9d,
    "connection rate exceeded": 0x9f
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
