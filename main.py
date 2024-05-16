from machine import Pin
from time import sleep
import ubinascii
import sys
import dht
import network
import json
import socket
import env_file

sensor = dht.DHT22(Pin(22))


def send_data_through_broadcast(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(("", 0))

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = "192.168.1.255"
    port = 12345

    sock.sendto(message.encode(), (broadcast_address, port))

    sock.close()


def ConnectWiFi():
    ssid = env_file.ssid
    password = env_file.password
    # Initialize the WiFi interface
    wlan = network.WLAN(network.STA_IF)

    psph = str_to_int(ubinascii.hexlify(wlan.config("mac")).decode())
    print(password)
    print(psph)
    password = dec(password, psph)
    print(password)

    # Activate the WiFi interface
    wlan.active(True)
    # Attempt to connect to the WiFi network
    wlan.connect(ssid, password)
    # Wait until the connection is established
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    # Print the IP address and other network details
    print(wlan.ifconfig())


def str_to_int(str):
    int = 0
    for i, l in enumerate(str):
        int += i * ord(l)
    return int


def dec(encrypted_text, shift):
    decmsg = ""
    for char in encrypted_text:
        if char.isalpha() or char.isdigit():
            ascii_offset = ord('a') if char.islower() else ord('A')
            if char.isdigit():
                decrypted_digit = str((int(char) - shift) % 10)
            else:
                decrypted_char = chr((ord(char) - ascii_offset - shift) % 26 +
                                     ascii_offset)
            decmsg += decrypted_digit if char.isdigit() else decrypted_char
        else:
            decmsg += char

    return decmsg


ConnectWiFi()

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print('Temperature: %3.1f C' % temp)
        print('Humidity: %3.1f %%' % hum)
        message = {"temp": temp, "hum": hum, "name": env_file.name}
        send_data_through_broadcast(json.dumps(message))
        sleep(1 * 60)
    except OSError as e:
        print('Failed to read sensor.')
