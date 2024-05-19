"""MQTT 5.0 exceptions."""


class MQTT5Exception(Exception):
    """MQTT 5.0 general exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MalformedPacketException(MQTT5Exception):
    """MQTT 5.0 malformed packet exception."""


class ProtocolErrorException(MQTT5Exception):
    """MQTT 5.0 protocol exception."""


class UnsupportedProtocolVersionException(MQTT5Exception):
    """MQTT 5.0 unsupported protocol version exception."""


class ClientIdNotValidException(MQTT5Exception):
    """MQTT 5.0 client id not valid exception."""


class BadUserNameOrPasswordException(MQTT5Exception):
    """MQTT 5.0 bad username or password exception."""


class NotAuthorizedException(MQTT5Exception):
    """MQTT 5.0 not authorized exception."""


class ServerUnavailableException(MQTT5Exception):
    """MQTT 5.0 server unavailable exception."""


class ServerBusyException(MQTT5Exception):
    """MQTT 5.0 server busy exception."""


class BannedException(MQTT5Exception):
    """MQTT 5.0 banned exception."""


class BadAuthenticationMethodException(MQTT5Exception):
    """MQTT 5.0 bad authentication method exception."""


class TopicNameInvalidException(MQTT5Exception):
    """MQTT 5.0 topic name invalid exception."""


class PacketTooLargeException(MQTT5Exception):
    """MQTT 5.0 packet too large exception."""


class QuotaExceededException(MQTT5Exception):
    """MQTT 5.0 quota exceeded exception."""


class PayloadFormatException(MQTT5Exception):
    """MQTT 5.0 payload format exception."""


class RetainNotSupportedException(MQTT5Exception):
    """MQTT 5.0 retain not supported exception."""


class QosNotSupportedException(MQTT5Exception):
    """MQTT 5.0 qos not supported exception."""


class UseAnotherServerException(MQTT5Exception):
    """MQTT 5.0 use another server exception."""


class ReceiveMaximumExceededException(MQTT5Exception):
    """MQTT 5.0 receive maximum exceeded exception."""


class ServerMovedException(MQTT5Exception):
    """MQTT 5.0 server moved exception."""


class ConnectionRateExceededException(MQTT5Exception):
    """MQTT 5.0 connection rate exceeded exception."""


class SharedSubscriptionNotSupportedException(MQTT5Exception):
    """MQTT 5.0 shared subscription not supported exception."""


class SubscriptionIdentifierNotSupportedException(MQTT5Exception):
    """MQTT 5.0 subscription identifier not supported exception."""


class WildcardSubscriptionNotSupportedException(MQTT5Exception):
    """MQTT 5.0 wildcard subscription not supported exception."""
