""" Test the packets that are sent to the broker. """
import sys
import unittest

sys.path.insert(1, ".")
from MQTT5.packets import ConnectUnpacker


class TestMQTT5Packets(unittest.TestCase):
    """ Test packets that are sent to the broker. """
    def test_connect(self) -> None:
        """ Test the CONNECT packet. """
        raw = (
            b'\x102\x00\x04MQTT\x05\xc0\x00<\x00\x00\x17mymqtt'
            b'-2770259619962042\x00\x07antonio\x00\x03aaa'
        )
        conn = ConnectUnpacker(raw)
        conn.unpack()
        self.assertEqual(conn.fixed_header, b'00010000')
        self.assertEqual(conn.protocol_name, b'MQTT')
        self.assertEqual(conn.protocol_version, 5)
        self.assertEqual(
            conn.connect_flags,
            {
                'username': True,
                'password': True,
                'will_retain': False,
                'will_qos': 0,
                'will_flag': False,
                'clean_start': False,
                'reserved': 0
            }
        )
        self.assertEqual(conn.keep_alive, 60)
        self.assertEqual(conn.properties_length, 0)
        self.assertEqual(conn.properties, {})
        self.assertEqual(conn.client_id, b'mymqtt-2770259619962042')
        self.assertEqual(conn.will_topic, None)
        self.assertEqual(conn.will_payload, None)
        self.assertEqual(conn.user_name, b'antonio')
        self.assertEqual(conn.password, b'aaa')

    def test_connect_no_username(self) -> None:
        """ Test the CONNECT packet without username. """
        raw =  b'\x10\x11\x00\x04MQTT\x05\x02\x00\x00\x00\x00\x04test'
        conn = ConnectUnpacker(raw)
        conn.unpack()
        self.assertEqual(conn.fixed_header, b'00010000')
        self.assertEqual(conn.protocol_name, b'MQTT')
        self.assertEqual(conn.protocol_version, 5)
        self.assertEqual(
            conn.connect_flags,
            {
                'username': False,
                'password': False,
                'will_retain': False,
                'will_qos': 0,
                'will_flag': False,
                'clean_start': True,
                'reserved': 0
            }
        )
        self.assertEqual(conn.keep_alive, 0)
        self.assertEqual(conn.properties_length, 0)
        self.assertEqual(conn.properties, {})
        self.assertEqual(conn.client_id, b'test')
        self.assertEqual(conn.will_topic, None)
        self.assertEqual(conn.will_payload, None)
        self.assertEqual(conn.user_name, None)
        self.assertEqual(conn.password, None)


if __name__ == "__main__":
    unittest.main()
