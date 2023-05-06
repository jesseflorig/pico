from machine import Pin, SPI
from mqtt import MQTTClient
from ubinascii import hexlify
import usocket as socket
import ustruct as struct
import network
import time
import json

STATUS_LED = Pin(25, Pin.OUT)
LED = Pin(0, Pin.OUT)
BUTTON = Pin(1, Pin.IN)

# ETHERNET
MOSI = Pin(19)
MISO = Pin(16)
SCK = Pin (18)
CS = Pin(17)
RESET = Pin(20)
PICO_IP = '192.168.0.91'
GATEWAY = '192.168.0.1'

# MQTT
MQTT_URI = '192.168.2.1'
CLIENT_ID = 'Pico'
MQTT_USER = 'pico'
MQTT_PASS = 'password'
TOPIC = 'pico/light/'

def eth_init():
    STATUS_LED.value(0) # Start with Status LED off
    spi = SPI(0, 2_000_000, mosi=MOSI, miso=MISO, sck=SCK)
    nic = network.WIZNET5K(spi, CS, RESET)
    nic.active(True)
    while not nic.isconnected():
        STATUS_LED.value(0) # Blink if still connecting
        time.sleep(1)
        STATUS_LED.value(1)
        print('Connecting...')
    local_ip = nic.ifconfig()[0]
    print(f'Connected as {local_ip}!')
    
def handle_message(topic,msg):
    print((topic, msg))

    # Set the LED value to "on" state
    val = json.loads(msg)['on']
    LED.value(val)
    
def handle_button(pin):
    print('button pressed')
    LED.toggle()
    
def mqtt_connect():
    client = MQTTClient(CLIENT_ID, MQTT_URI, user=MQTT_USER, password=MQTT_PASS, keepalive=60000)
    client.connect()
    print(f'Connected to MQTT broker @ {MQTT_URI}!')
    
    client.set_callback(handle_message)
    client.subscribe(TOPIC)
    
    return client

def reconnect():
    print('Failed to connect to MQTT broker @ {MQTT_URI}. Reconnecting...')
    time.sleep(5)
    machine.reset()

def main():
    eth_init()
    
    try:
        client = mqtt_connect()
    except OSError as e:
        reconnect()
    
    # Setup button interrupt
    BUTTON.irq(trigger=Pin.IRQ_RISING, handler=handle_button)
    
    while True:
        try:
            client.check_msg()
        except OSError as e:
            reconnect()
            
        #msg = json.dumps({ 'on': LED.value() })
        #client.publish(TOPIC, msg)
        #time.sleep(5)
        
if __name__ == "__main__":
    main()