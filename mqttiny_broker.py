""" MicroPython MQTT Broker. """
import network
import socket
import select
import uasyncio as asyncio
import ujson as json
import utime as time


WIFI_SSID = "your_ssid_here"
WIFI_PASSWORD = "your_password_here"

BROKER_HOST = "0.0.0.0"
BROKER_PORT = 1883
UPDATE_INTERVAL = 10

CONNECT = hex(0x10)
PUBLISH = hex(0x30)
SUBSCRIBE = hex(0x82)
UNSUBSCRIBE = hex(0x3e)
DISCONNECT = hex(0xe0)
PINGREQ = hex(0xc0)
ABRUPT_DISCONNECT = b""

CONNACK = (
    b"\x20\x13\x00\x00\x10\x27\x00\x10\x00\x00\x25\x00"
    b"\x2a\x00\x29\x00\x22\xff\xff\x28\x01"
)
PUBACK = b"\x40\x04\x64\x4a\x10\x00"
PINGRESP = b"\xd0\x00"
SUBACK = b"\x90\x04\x00\x00\x00\x02"


class MQTTinyBroker:
    """ MicroPython MQTT Broker. """
    def __init__(
        self,
        wifi_ssid: str,
        wifi_password: str,
        broker_host: str,
        broker_port: int,
        update_interval: int
    ) -> None:
        self.broker_version = "1.0"
        self.broker_start_time = time.time()
        self.sockets_list = []
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.update_interval = update_interval
        self.server_socket = None
        self.event_loop = None
        self.topics = {
            "$SYS/broker/version": [self.broker_version, []],
            "$SYS/broker/uptime": ["", []],
            "$SYS/broker/clients/total": ["", []],
            "$SYS/broker/clients/inactive": ["", []],
            "$SYS/broker/clients/disconnected": ["", []],
            "$SYS/broker/clients/active": ["", []],
            "$SYS/broker/clients/connected": ["", []],
            "$SYS/broker/clients/expired": ["", []],
            "$SYS/broker/clients/maximum": ["", []],
            "$SYS/broker/messagges/stored": ["", []],
            "$SYS/broker/messages/received": ["", []],
            "$SYS/broker/messages/sent": ["", []],
            "$SYS/broker/load/messages/received/1min": ["", []],
            "$SYS/broker/load/messages/received/5min": ["", []],
            "$SYS/broker/load/messages/received/15min": ["", []],
            "$SYS/broker/load/messages/sent/1min": ["", []],
            "$SYS/broker/load/messages/sent/5min": ["", []],
            "$SYS/broker/load/messages/sent/15min": ["", []],
            "$SYS/broker/load/connections/1min": ["", []],
            "$SYS/broker/load/connections/5min": ["", []],
            "$SYS/broker/load/connections/15min": ["", []],
            "$SYS/broker/load/bytes/received/1min": ["", []],
            "$SYS/broker/load/bytes/received/5min": ["", []],
            "$SYS/broker/load/bytes/received/15min": ["", []],
            "$SYS/broker/load/bytes/sent/1min": ["", []],
            "$SYS/broker/load/bytes/sent/5min": ["", []],
            "$SYS/broker/load/bytes/sent/15min": ["", []],
            "$SYS/broker/load/publish/dropped/1min": ["", []],
            "$SYS/broker/load/publish/dropped/5min": ["", []],
            "$SYS/broker/load/publish/dropped/15min": ["", []],
            "$SYS/broker/load/publish/received/1min": ["", []],
            "$SYS/broker/load/publish/received/5min": ["", []],
            "$SYS/broker/load/publish/received/15min": ["", []],
            "$SYS/broker/load/publish/sent/1min": ["", []],
            "$SYS/broker/load/publish/sent/5min": ["", []],
            "$SYS/broker/load/publish/sent/15min": ["", []],
            "$SYS/broker/load/socket/1min": ["", []],
            "$SYS/broker/load/socket/5min": ["", []],
            "$SYS/broker/load/socket/15min": ["", []],
            "$SYS/broker/store/messages/count": ["", []],
            "$SYS/broker/store/messages/bytes": ["", []],
            "$SYS/broker/subscriptions/count": ["", []],
            "$SYS/broker/shared_subscriptions/count": ["", []],
            "$SYS/broker/retained_messages/count": ["", []],
            "$SYS/broker/publish/messages/dropped": ["", []],
            "$SYS/broker/publish/messages/received": ["", []],
            "$SYS/broker/publish/messages/sent": ["", []],
            "$SYS/broker/publish/bytes/received": ["", []],
            "$SYS/broker/publish/bytes/sent": ["", []],
            "$SYS/broker/bytes/received": ["", []],
            "$SYS/broker/bytes/sent": ["", []],
        }
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.wifi.connect(wifi_ssid, wifi_password)
        print("Connecting to WiFi...")
        while not self.wifi.isconnected():
            pass

    def _handle_connect(
        self,
        client_socket: socket.socket,
        address: tuple
    ) -> None:
        """ Handle new client connection. """
        data = client_socket.recv(1024)
        if hex(data[0]) != CONNECT:
            print("Invalid connection request", data, address)
            client_socket.close()
            return
        self.sockets_list.append(client_socket)
        print(
            "\n\n> received CONNECT",
            "\n> packet: ", data,
            "\n> ip:port: ", address
        )
        client_socket.sendall(CONNACK)
        print(
            "\n\n> sent CONNACK",
            "\n> packet: ", CONNACK,
            "\n> ip:port: ", address
        )

    def _handle_disconnect(
        self,
        client_socket: socket.socket
    ) -> None:
        """ Handle client disconnect. """
        print("Client disconnected")
        client_socket.close()
        self.sockets_list.remove(client_socket)

    def handle_pingreq(self, client_socket: socket.socket, data: bytes) -> None:
        """ Handle client ping request. """
        print("\n\n> received PINGREQ", "\n> packet: ", data)
        client_socket.sendall(PINGRESP)
        print("\n\n> Sent PINGRESP", "\n> packet: ", PINGRESP)

    def _handle_subscribe(
        self,
        data: bytes,
        client_socket: socket.socket
    ) -> None:
        """ Handle client subscribe request. """
        topic_length = data[5]
        topic = data[6:6 + topic_length].decode()
        print(
            "\n\n> received SUBSCRIBE",
            "\n> packet: ", data,
            "\n> topic: ", topic
        )
        if topic not in self.topics:
            self.topics[topic] = ["", []]
        if client_socket not in self.topics[topic][1]:
            self.topics[topic][1].append(client_socket)
        client_socket.sendall(SUBACK)

    def _handle_publish(
        self,
        data: bytes,
        client_socket: socket.socket,
    ) -> None:
        """ Handle client publish request. """
        topic_length = data[3]
        topic = data[4:4 + topic_length].decode()
        message = data[4 + topic_length:].decode()
        client_socket.sendall(PUBACK)
        print(
            "\n\n> received PUBLISH",
            "\n> packet: ", data,
            "\n> topic: ", topic,
            "\n> message: ", message
        )
        if topic not in self.topics:
            self.topics[topic] = ["", []]
        self.topics[topic][0] = message
        subscribers_sockets = self.topics[topic][1]
        for subscriber_socket in subscribers_sockets:
            print(
                "Sending to subscriber:",
                subscriber_socket,
                "message",
                bytes(data, 'utf-8')
            )
            subscriber_socket.sendall(data)

    def _handle_client_incoming_data(
        self,
        client_socket: socket.socket
    ) -> None:
        """ Handle incoming data from a client. """
        try:
            data = client_socket.recv(1024)
            print("Received data from client", data)
            command = hex(data[0])
            if command == SUBSCRIBE:
                self._handle_subscribe(data, client_socket)
                return
            if command == PUBLISH:
                self._handle_publish(data, client_socket)
                return
            if command == DISCONNECT:
                self._handle_disconnect(client_socket)
                return
            if command == PINGREQ:
                self.handle_pingreq(client_socket, data)
                return
            print("Unsupported command:", command)
        except IndexError as err:
            print("Error handling client data:", err)

    async def update_default_topics(self) -> None:
        """ Update default topics with new values. """
        while True:
            uptime = time.time() - self.broker_start_time
            self.topics["$SYS/broker/uptime"][0] = uptime
            self.topics["$SYS/broker/clients/total"][0] = len(
                self.sockets_list
            )
            await asyncio.sleep(self.update_interval)

    def start(self) -> None:
        """ Start the MQTT broker. """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.broker_host, self.broker_port))
        self.server_socket.listen(5)
        print(
            "MicroMQTTBroker listening on", self.broker_host,
            "port", self.broker_port,
            "broker ip:", self.wifi.ifconfig()[0]
        )
        self.sockets_list = [self.server_socket]
        self.event_loop = asyncio.get_event_loop()
        self.event_loop.create_task(self.update_default_topics())
        while True:
            read_sockets, _, _ = select.select(self.sockets_list, [], [])
            for sock in read_sockets:
                if sock == self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    self._handle_connect(client_socket, address)
                else:
                    self._handle_client_incoming_data(sock)

    def stop(self) -> None:
        """ Stop the MQTT broker. """
        for sock in self.sockets_list[1:]:
            sock.close()
        self.server_socket.close()
        self.event_loop.close()
        self.wifi.disconnect()
        self.wifi.active(False)


if __name__ == "__main__":
    broker = MQTTinyBroker(
        WIFI_SSID,
        WIFI_PASSWORD,
        BROKER_HOST,
        BROKER_PORT,
        UPDATE_INTERVAL
    )
    try:
        broker.start()
    except Exception as e:
        print("Stopping broker due to an unhandled exception: ", e)
        broker.stop()
    finally:
        broker.stop()
