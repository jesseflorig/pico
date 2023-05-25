from machine import Pin, PWM
from fleet1 import Fleet1Client
import time
import json

# Sensors
LED = Pin(25, Pin.OUT)
EXT_LED = Pin(0, Pin.OUT)
PWM_LED = PWM(EXT_LED)
PWM_LED.freq(1_000)
last_on_percent = 1.0

CLIENT_ID = 'pico'
MQTT_USER = 'pico'
MQTT_PASS = 'password'

TOPICS = [
    'pico/light/',
    'pico/light2/'
    ]

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

last_time = 0
last_on_percent = 1
if __name__ == "__main__":
    client = Fleet1Client(CLIENT_ID, user=MQTT_USER, password=MQTT_PASS, topics=TOPICS, callback=handle_message)
    client.connect()
    
    def debounce(callback):
        global last_time
        current_time = time.ticks_ms()
        if (time.ticks_diff(current_time, last_time) > 500):
            last_time = current_time
            callback()
            
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
          
    def toggle_pwm_led():
            global last_on_percent
            if PWM_LED.duty_u16() is not 0:
                fade_led(0)
                client.publish(b'pico/light2/', b'{"on": 0}')
            else:
                fade_led(last_on_percent)
                msg = json.dumps({ "on" : last_on_percent }).encode('utf-8')
                client.publish(b'pico/light2/', msg)
                
    def handle_pwm_button(pin):
        if (pin.value() == 0):
            debounce(toggle_pwm_led)
            
    # Create Button tuples
    buttons = [
        (1, handle_pwm_button)
    ]
    
    client.register_buttons(buttons)
    client.listen()

