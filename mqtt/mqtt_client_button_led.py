from machine import Pin, SPI
from mqtt import MQTTClient
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
TOPICS = [
    'pico/light/',
    'pico/light2/'
    ]

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
    client.connect()
    print(f'Connected to MQTT broker @ {MQTT_URI}!')
    
    client.set_callback(handle_message)
    
    for topic in TOPICS:
        print(f'Subscribing to {topic}...')
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
        
    def handle_button(pin):
        DEBOUNCE_INTERVAL = 500
        last_debounce = 0
        
        if ((pin.value() is 0) and (time.ticks_ms()-last_debounce) > DEBOUNCE_INTERVAL):
            print('Button pressed!')
            client.publish(b'pico/button', b'{"press": 1}')
            last_debounce=time.ticks_ms()
    
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
