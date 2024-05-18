"""CircuitPython MQTT example for Fleet1"""
import os
import time
import board
import busio
import neopixel
import adafruit_connection_manager
import adafruit_requests as requests
import adafruit_wiznet5k.adafruit_wiznet5k_socketpool as socket
from digitalio import DigitalInOut
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
from adafruit_minimqtt.adafruit_minimqtt import MQTT

# Initial state
print("\nMQTT Client Test")
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.fill((255, 255, 0))  # Yellow

# Init ethernet
cs = DigitalInOut(board.D10)
spi_bus = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
eth = WIZNET5K(spi_bus, cs)

pool = adafruit_connection_manager.get_radio_socketpool(eth)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(eth)
requests = requests.Session(pool, ssl_context)

TEST_URL = "http://192.169.1.211:1880/hello"
ATTEMPTS = 4

print("Fetching text from %s" % TEST_URL)
with requests.get(TEST_URL) as response:
    print("-" * 40)
    print("Text Response: ", response.text)
    print("-" * 40)

response.close()
