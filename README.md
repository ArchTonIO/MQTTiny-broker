# MQTTiny Broker - A tiny MQTT broker for embedded systems

This project is a work in progress, it was only tested with the RP2040 microcontroller (Raspberry Pi Pico).

The aim is to be compatible with both MQTT 3.1.1 and 5.0 protocols, but now i'm only working on 5.0, seems that lot of clients still uses 3.1.1 so i will implement it later.

This broker must remain pretty simple and lightweight software, so it can be used on embedded systems with limited resources, and, first of all, it must be easy to use and understand without overengineering stuff (stop overengineering stuff please).

By today the only working things are:

    - CONNECT
    - CONNACK
    - PINGREQ
    - PINGRESP
    - DISCONNECT

so basically an MQTT 5.0 client can connect and stay connected with the broker, more coming soon.

TESTED WITH THIS CLIENTS:

    - [Paho MQTT python client](https://pypi.org/project/paho-mqtt/)
    - [MQTT Explorer](https://mqtt-explorer.com/)
    - [MyMqtt for android](https://play.google.com/store/apps/details?id=at.tripwire.mqtt.client)

## TODO

- [x] Implement CONNECT
- [x] IMPLEMENT CONNACK
- [x] Implement PINGREQ
- [x] Implement PINGRESP
- [x] Implement DISCONNECT
- [ ] Implement PUBLISH
- [ ] Implement PUBACK
- [ ] Implement PUBREC
- [ ] Implement PUBREL
- [ ] Implement PUBCOMP
- [ ] Implement SUBSCRIBE
- [ ] Implement SUBACK
- [ ] Implement UNSUBSCRIBE
- [ ] Implement UNSUBACK
- [ ] Implement wildcard subscriptions
- [ ] Implement MQTT 3.1.1 protocol

---------------------------------------------- <--- line of the realistic goals

- [ ] Implement QoS 1 and 2
- [ ] Implement Retained messages
- [ ] implement authentication
- [ ] dump to sd card
- [ ] implement TLS
