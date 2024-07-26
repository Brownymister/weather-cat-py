# source: https://github.com/raspberrypi/pico-micropython-examples/blob/master/bluetooth/picow_ble_temp_sensor.py

import bluetooth
import random
import struct
import time
import machine
import ubinascii
import dht
from blauzahn_advert import advertising_payload
from micropython import const
from machine import Pin
import env_file

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR, ),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

sensor = dht.DHT22(Pin(22))


class BLETemperature:

    def __init__(self, ble, name="WeatherCat"):
        self._sensor_temp = machine.ADC(4)
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle, ), ) = self._ble.gatts_register_services(
            (_ENV_SENSE_SERVICE, ))
        self._connections = set()
        self.name = env_file.name
        if len(name) == 0:
            name = 'Pico %s' % ubinascii.hexlify(
                self._ble.config('mac')[1], ':').decode().upper()
        print('Sensor name %s' % name)
        self._payload = advertising_payload(name=name,
                                            services=[_ENV_SENSE_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def update_temperature(self, notify=False, indicate=False):
        # Write the local value, ready for a central to read.
        temp_deg_c, hum = self.get_temp()
        print("write temp %.2f degc" % temp_deg_c)
        # self._ble.gatts_write(self._handle,
        #                       struct.pack("<h", int(temp_deg_c * 100)))

        self._ble.gatts_write(
            self._handle, '{"t":' + str(temp_deg_c) + ',"h":' + str(hum) +
            ', "name":"' + self.name + '"}')
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, self._handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    # ref https://github.com/raspberrypi/pico-micropython-examples/blob/master/adc/temperature.py
    def get_temp(self):
        sensor.measure()
        return sensor.temperature(), sensor.humidity()


def demo():
    ble = bluetooth.BLE()
    temp = BLETemperature(ble)
    led = Pin('LED', Pin.OUT)
    while True:
        led.toggle()
        time.sleep_ms(1000)
        temp.update_temperature(notify=True, indicate=False)
        led.toggle()
        time.sleep_ms(1000 * 59)


# def encrypt_msg(message):
#     with open("public_key.pem", "rb") as public_file:
#         public_key = serialization.load_pem_public_key(
#             public_file.read(), backend=default_backend())
#     encrypted = public_key.encrypt(
#                      label=None))
#
#     return encrypted

if __name__ == "__main__":
    demo()
