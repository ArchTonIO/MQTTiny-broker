""" MicroPython MQTT Broker. """
import select
import socket
import sys

import network
import uasyncio as asyncio
import utime as time

from default_topics import default_topics
from MQTT5.packets import (
    ConnackPacker,
    ConnectUnpacker,
    PublishUnpacker,
    SubscribeUnpacker,
    handle_mqtt5_protocol_errors,
)

WIFI_SSID = "VodafoneTPS"
WIFI_PASSWORD = "kingoflamas99"

BROKER_HOST = "0.0.0.0"
BROKER_PORT = 1883
UPDATE_INTERVAL = 10

CONNECT = hex(0x10)
PUBLISH = hex(0x30)
SUBSCRIBE = hex(0x82)
UNSUBSCRIBE = hex(0x3e)
DISCONNECT = hex(0xe0)
ABRUPT_DISCONNECT = b""
PINGREQ = hex(0xc0)
PINGRESP = b"\xd0\x00"


class MQTTinyBroker:
    """ MicroPython MQTT Broker. """
    def __init__(
        self,
        wifi_ssid: str,
        wifi_password: str,
        broker_host: str,
        broker_port: int,
        update_interval: int,
        debug: bool = False
    ) -> None:
        self.broker_version = "1.0"
        self.broker_start_time = time.time()
        self.sockets_list = []
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.update_interval = update_interval
        self.server_socket = None
        self.event_loop = None
        self.topics = default_topics
        self.topics["$SYS/broker/version"][0] = self.broker_version
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.wifi.connect(wifi_ssid, wifi_password)
        self.large_packet = b""
        self.debug = debug
        print("Connecting to WiFi...")
        while not self.wifi.isconnected():
            pass

    @handle_mqtt5_protocol_errors
    def _handle_connect(
        self,
        client_socket: socket.socket,
        address: tuple
    ) -> None:
        """ Handle new client connection. """
        data = client_socket.recv(1024)
        if hex(data[0]) != CONNECT:
            print("\n\n ## INVALID CONNECTION REQUEST ##", data, address)
            client_socket.close()
            return
        connect = ConnectUnpacker(data)
        connect.unpack()
        self.sockets_list.append(client_socket)
        print(
            "\n\n## RECEIVED CONNECT ##",
            "\n> packet: ", data,
            "\n> ip, port: ", address,
            "\n> id: ", connect.client_id.decode(),
            "\n> user: ", connect.user_name.decode() if connect.user_name else None,
            "\n> password: ", connect.password.decode() if connect.password else None,
        )
        if self.debug:
            print(connect)
        connack = ConnackPacker(
            session_present=False,
            reason_code="success"
        )
        client_socket.sendall(connack.pack())
        print(
            "\n\n## SENT CONNACK ##",
            "\n> packet: ", connack.raw,
            "\n> ip:port: ", address,
            "\n> reason code: ", connack.reason_code
        )
        if self.debug:
            print(connack)

    def _handle_disconnect(self, client_socket: socket.socket) -> None:
        """ Handle client disconnect. """
        print("Client disconnected")
        client_socket.close()
        self.sockets_list.remove(client_socket)

    def handle_pingreq(
        self,
        client_socket: socket.socket,
        data: bytes
    ) -> None:
        """ Handle client ping request. """
        print("\n\n## RECEIVED PINGREQ ##", "\n> packet: ", data)
        client_socket.sendall(PINGRESP)
        print("\n\n## SENT PINGRESP ##", "\n> packet: ", PINGRESP)

    @handle_mqtt5_protocol_errors
    def _handle_subscribe(
        self,
        data: bytes,
        client_socket: socket.socket
    ) -> None:
        """ Handle client subscribe request. """
        subscribe = SubscribeUnpacker(data)
        subscribe.unpack()
        print(
            "\n\n## RECEIVED SUBSCRIBE ##",
            "\n> packet: ", subscribe.raw,
            "\n> topic: ", subscribe.topic.decode()
        )
        if subscribe.topic not in self.topics:
            self.topics[subscribe.topic] = ["", []]
        if client_socket not in self.topics[subscribe.topic][1]:
            self.topics[subscribe.topic][1].append(client_socket)
        client_socket.sendall("")

    @handle_mqtt5_protocol_errors
    def _handle_publish(self, data: bytes) -> None:
        """ Handle client publish request. """
        publish = PublishUnpacker(data)
        publish.unpack()
        print(
            "\n\n## RECEIVED PUBLISH ##",
            "\n> packet: ", data,
            "\n> topic: ", publish.topic.decode(),
            "\n> properties: ", publish.properties,
            "\n> payload: ", publish.payload.decode()
        )
        if self.debug:
            print(publish)
        if publish.topic not in self.topics:
            self.topics[publish.topic] = ["", []]
        self.topics[publish.topic][0] = publish.payload
        subscribers_sockets = self.topics[publish.topic][1]
        for subscriber_socket in subscribers_sockets:
            print(
                "\n\n## SENDING PUBLISH ",
                f"TO SUBSCRIBERS OF TOPIC {publish.topic.decode()} ##",
                f"\n> message: {publish.payload.decode()}"
            )
            subscriber_socket.sendall(data)

    def _handle_client_incoming_data(
        self,
        client_socket: socket.socket
    ) -> None:
        """ Handle incoming data from a client. """
        try:
            data = client_socket.recv(1024)
            if data == ABRUPT_DISCONNECT:
                self._handle_disconnect(client_socket)
                return
            command = hex(data[0])
            if command == SUBSCRIBE:
                self._handle_subscribe(data, client_socket)
                return
            if command == PUBLISH:
                self._handle_publish(data)
                return
            if command == DISCONNECT:
                self._handle_disconnect(client_socket)
                return
            if command == PINGREQ:
                self.handle_pingreq(client_socket, data)
                return
            print("Unsupported command:", command)
        except IndexError as err:
            print("Error handling client data:", data)
            sys.print_exception(err)

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
            "MQTTiny listening on:", self.broker_host,
            "port:", self.broker_port,
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
        UPDATE_INTERVAL,
        debug=False
    )
    try:
        broker.start()
    except Exception as e:
        print("Stopping broker due to an unhandled exception")
        sys.print_exception(e)
        broker.stop()
    finally:
        broker.stop()
