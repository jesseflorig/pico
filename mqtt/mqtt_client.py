from machine import Pin
from fleet1 import Fleet1Client
import json

# Sensors
LED = Pin(25, Pin.OUT)

CLIENT_ID = 'pico'
MQTT_USER = 'pico'
MQTT_PASS = 'password'

TOPICS = [
    'pico/light/'
    ]
    
def handle_message(topic,msg):
    print(f'Rec\'d {msg.decode()} on \'{topic.decode()}\'')

    if topic == b'pico/light/':
        # Set the LED to "on" value
        val = json.loads(msg)['on']
        LED.value(val)
    else:
        print(f'No handler for \'{topic.decode()}\'!')
        
if __name__ == "__main__":
    client = Fleet1Client(CLIENT_ID, user=MQTT_USER, password=MQTT_PASS, topics=TOPICS, callback=handle_message)
    client.connect()
    client.listen()