from machine import Pin
from utime import sleep
# Initialisierung von GPIO13 als Ausgang
led = Pin(13, Pin.OUT)
# Wiederholung (Endlos-Schleife)
while True:
    # LED einschalten
    led.on()
    # halbe Sekunde warten
    sleep(0.5)
    # LED ausschalten
    led.off()
    # 1 Sekunde warten
    sleep(1)
