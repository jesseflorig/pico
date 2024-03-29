from machine import Pin, PWM, SPI
from mqtt import MQTTClient, MQTTException
import network
import time
import json

#SENSORS
LED = Pin(25, Pin.OUT)
EXT_LED = Pin(0, Pin.OUT)
PWM_LED = PWM(EXT_LED)
PWM_LED.freq(1_000)
last_on_percent = 1.0

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

# BUTTON PRESS
DEBOUNCE_DELAY = 50
SINGLE_PRESS = 100
LONG_PRESS = 800

def eth_init():
    spi = SPI(0, 2_000_000, mosi=MOSI, miso=MISO, sck=SCK)
    nic = network.WIZNET5K(spi, CS, RESET)
    nic.active(True)
    print(f'Connecting...')
    
    # Blink onboard LED while connecting
    while not nic.isconnected():
        LED.value(1)
        time.sleep(1)
        LED.value(0)
        time.sleep(1)
    
    local_ip = nic.ifconfig()[0]
    print(f'Joined network as {local_ip}!')
    LED.value(1)

def fade_led(target_percent):
    global last_on_percent
    current_duty = PWM_LED.duty_u16()
    end_duty = int(65_536 * target_percent)
    step = 1 if current_duty < end_duty else -1
    # Add step to end duty to make it an inclusive range
    for duty in range(current_duty, end_duty + step, step):
        PWM_LED.duty_u16(duty)
    # Save last ON state
    if target_percent > 0:
        last_on_percent = target_percent

def handle_message(topic,msg):
    print(f'Rec\'d {msg.decode()} on \'{topic.decode()}\'')

    if topic == b'pico/light/':
        # Set the LED to "on" value
        val = json.loads(msg)['on']
        LED.value(val)
    if topic == b'pico/light2/':
        # Set the LED to "on" value
        try:
            val = json.loads(msg)['on']
        except:
            print('Ignoring malformed JSON')
        else:
            fade_led(val)
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
    
    def toggle_pwm_led():
        global last_on_percent
        if PWM_LED.duty_u16() is not 0:
            fade_led(0)
            client.publish(b'pico/light2/', b'{"on": 0}')
        else:
            fade_led(last_on_percent)
            msg = json.dumps({ "on" : last_on_percent }).encode('utf-8')
            client.publish(b'pico/light2/', msg)
        
    def handle_button(pin):
        if (pin.value() == 0):
            debounce(toggle_pwm_led)
            
    def single_press():
        print('!')
        
    def double_press():
        print('!!')
        
    def long_press():
        print('_!_')
    
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
