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

# Init MQTT
MQTT_BROKER = "http://192.169.1.211:1880"
MQTT_USERNAME = "pico"
MQTT_PASSWORD = "password"

mqtt_client = MQTT.MQTT(
    broker=MQTT_BROKER,
    username=MQTT_USERNAME,
    password=MQTT_PASSWORD,
    is_ssl=False,
    socket_pool=pool,
    ssl_context=ssl_context,
)

print("Connecting to Vanlab broker: %s..." % MQTT_BROKER)
