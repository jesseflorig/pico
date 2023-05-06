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
MQTT_URI = '172.20.1.152'
CLIENT_ID = 'Pico'
MQTT_USER = 'pico'
MQTT_PASS = 'password'
TOPIC = 'pico/light/'

def eth_init():
    spi = SPI(0, 2_000_000, mosi=MOSI, miso=MISO, sck=SCK)
    nic = network.WIZNET5K(spi, CS, RESET)
    nic.active(True)
    while not nic.isconnected():
        time.sleep(1)
        print('Connecting...')
    local_ip = nic.ifconfig()[0]
    print(f'Connected as {local_ip}!')
    LED.value(1)
    
def handle_message(topic,msg):
    print((topic, msg))

    # Set the LED value to "on" state
    val = json.loads(msg)['on']
    LED.value(val)
    
def handle_button(pin):
    print(pin)
    
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
    button = Pin(0, Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=handle_button)
    
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