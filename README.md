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
    - PUBLISH

so basically an MQTT 5.0 client can connect, stay connected with the broker and publish messages, more coming soon.

## TESTED WITH

- [Paho MQTT python client](https://pypi.org/project/paho-mqtt/)
- [MyMqtt for android](https://play.google.com/store/apps/details?id=at.tripwire.mqtt.client)

## TODO

- [x] Implement CONNECT
- [x] IMPLEMENT CONNACK
- [x] Implement PINGREQ
- [x] Implement PINGRESP
- [x] Implement DISCONNECT
- [x] Implement PUBLISH
- [ ] Implement SUBSCRIBE
- [ ] Implement UNSUBSCRIBE
- [ ] Implement wildcard subscriptions

---------------------------------------------- <--- line of the realistic goals

- [ ] Implement MQTT 3.1.1 protocol
- [ ] Implement QoS 1 and 2
  - [ ] PUBACK
  - [ ] PUBREC
  - [ ] PUBREL
  - [ ] PUBCOMP
  - [ ] SUBACK
  - [ ] UNSUBACK
- [ ] Implement Retained messages
- [ ] implement authentication
- [ ] dump to sd card
- [ ] implement TLS
