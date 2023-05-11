from machine import Pin, SPI
from mqtt import MQTTClient, MQTTException
import network
import time
import json

#SENSORS
LED = Pin(25, Pin.OUT)
EXT_LED = Pin(0, Pin.OUT)

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
    'pico/light/',
    'pico/light2/'
    ]

def eth_init():
    spi = SPI(0, 2_000_000, mosi=MOSI, miso=MISO, sck=SCK)
    nic = network.WIZNET5K(spi, CS, RESET)
    nic.active(True)
    print(f'Connecting...')
    
    while not nic.isconnected():
        time.sleep(1)
    
    local_ip = nic.ifconfig()[0]
    print(f'Joined network as {local_ip}!')
    LED.value(1)
    
def handle_message(topic,msg):
    print(f'Rec\'d {msg.decode()} on \'{topic.decode()}\'')

    if topic == b'pico/light/':
        # Set the LED to "on" value
        val = json.loads(msg)['on']
        LED.value(val)
    if topic == b'pico/light2/':
        # Set the LED to "on" value
        val = json.loads(msg)['on']
        EXT_LED.value(val)
    else:
        print(f'No handler for \'{topic.decode()}\'!')
    
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

last_time = 0
def main():
    eth_init()
    
    try:
        client = mqtt_connect()
    except OSError as e:
        reconnect()
    else:
        client.publish(STATUS_TOPIC, CONNECT_MSG)
    
    def debounce(callback):
        global last_time
        current_time = time.ticks_ms()
        if (time.ticks_diff(current_time, last_time) > 500):
            last_time = current_time
            callback()
    
    def toggle_led():
        EXT_LED.toggle()
        
        if EXT_LED.value() is 0:
            client.publish(b'pico/light2/', b'{"on": 0}')
        else:
            client.publish(b'pico/light2/', b'{"on": 1}')
        
    def handle_button(pin):
        if (pin.value() == 0):
            debounce(toggle_led)
    
    # Setup button interrupt
    button = Pin(1, Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=handle_button)
    
    while True:
        try:
            client.wait_msg()
        except OSError as e:
            reconnect()
            
    client.disconnect()
        
if __name__ == "__main__":
    main()
