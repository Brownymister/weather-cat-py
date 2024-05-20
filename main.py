from machine import Pin, deepsleep, lightsleep
import time
import ubinascii
import sys
import dht
import network
import json
import socket
import env_file

sensor = dht.DHT22(Pin(22))
led = Pin(13, Pin.OUT)

unique_id = ""


def log(text):
    with open('log.txt', 'a') as file:
        # Write the string to the file
        file.write(text + "\n")


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
    led.on()
    time.sleep(0.5)
    led.off()

    log("i am here")

    mac_adrr = ubinascii.hexlify(wlan.config("mac")).decode()
    s = machine.unique_id()

    unique_id = ""
    for b in s:
        unique_id += str(int(hex(b)[2:], 16))

    log("chip_id: " + unique_id)
    password = dec(password, int(unique_id))

    # Activate the WiFi interface
    wlan.active(True)
    # Attempt to connect to the WiFi network
    wlan.connect(ssid, password)
    # Wait until the connection is established
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        log('Waiting for connection...')
        time.sleep(1)
    # Print the IP address and other network details
    led.on()
    time.sleep(0.5)
    led.off()
    print(wlan.ifconfig())
    return unique_id


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


# def get_time_stamp():
#     try:
#         ntptime.settime()
#         current_time = time.localtime()
#         return "{:02d}/{:02d}/{} {:02d}:{:02d}".format(current_time[2],
#                                                        current_time[1],
#                                                        current_time[0],
#                                                        current_time[3],
#                                                        current_time[4])
#     except:
#         return "TIME_ERROR"


def main():
    unique_id = ConnectWiFi()

    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print('Temperature: %3.1f C' % temp)
    print('Humidity: %3.1f %%' % hum)

    message = {
        "temp": temp,
        "hum": hum,
        "name": env_file.name,
        "unique_id": str(unique_id)
    }
    log(json.dumps(message))
    send_data_through_broadcast(json.dumps(message))
    lightsleep(1000 * 60 * 60)


while True:
    main()
