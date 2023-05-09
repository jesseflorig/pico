from machine import Pin, SPI
from mqtt import MQTTClient
import network
import time
import json

#SENSORS
LED = Pin(25, Pin.OUT)

# ETHERNET
MOSI = Pin(19)
MISO = Pin(16)
SCK = Pin (18)
CS = Pin(17)
RESET = Pin(20)

# MQTT
MQTT_URI = '192.169.1.211'
CLIENT_ID = 'Pico'
MQTT_USER = 'pico'
MQTT_PASS = 'password'

STATUS_TOPIC = b'pico/status'
CONNECT_MSG = b'{"connected": 1}'
DISCONNECT_MSG = b'{"connected": 0}'

SUB_TOPICS = [
    'pico/light/'
    ]

def eth_init():
    spi = SPI(0, 2_000_000, mosi=MOSI, miso=MISO, sck=SCK)
    nic = network.WIZNET5K(spi, CS, RESET)
    nic.active(True)
    while not nic.isconnected():
        time.sleep(1)
        print('Connecting...')
    
    local_ip = nic.ifconfig()[0]
    print(f'Joined network as {local_ip}!')
    LED.value(1)
    
def handle_message(topic,msg):
    print(f'Rec\'d {msg.decode()} on \'{topic.decode()}\'')

    if topic == b'pico/light/':
        # Set the LED to "on" value
        val = json.loads(msg)['on']
        LED.value(val)
    else:
        print(f'No handler for \'{topic.decode()}\'!')
    
def handle_button(pin):
    print(pin)
    
def mqtt_connect():
    client = MQTTClient(CLIENT_ID, MQTT_URI, user=MQTT_USER, password=MQTT_PASS, keepalive=60000)
    client.set_last_will(STATUS_TOPIC, DISCONNECT_MSG)
    
    try:
        client.connect()
    except MQTTException as e:
        print(e)
    else:
        print(f'Connected to MQTT broker @ {MQTT_URI}!')
    
    client.set_callback(handle_message)
    
    for topic in SUB_TOPICS:
        print(f'Subscribed to {topic}...')
        client.subscribe(topic)
    
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
    
    while True:
        try:
            client.check_msg()
        except OSError as e:
            reconnect()
        
if __name__ == "__main__":
    main()