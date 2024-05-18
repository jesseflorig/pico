from machine import Pin, SPI
from mqtt import MQTTClient
import network
import time

class Fleet1Client:
    def __init__(
        self,
        client_id,
        user=None,
        password=None,
        topics=[],
        callback=None
    ):
        self.client = None
        self.mqtt_uri = '192.169.1.211'
        self.client_id = client_id
        self.user = user
        self.pswd = password
        self.topics = topics
        self.status_topic = f'fleet1/{client_id}/status'.encode('utf-8')
        self.connect_msg = b'{"connected": 1}'
        self.disconnect_msg = b'{"connected": 0}'
        self.keepalive = 60000
        self.callback=callback
        self.buttons = []

    def eth_init(self):
        led = Pin(25, Pin.OUT)
        spi = SPI(0, 2_000_000, mosi=Pin(19), miso=Pin(16), sck=Pin(18))
        nic = network.WIZNET5K(spi, Pin(17), Pin(20))
        nic.active(True)
        print(f'Connecting...')
    
        # Blink onboard LED while connecting
        while not nic.isconnected():
            led.value(1)
            time.sleep(1)
            led.value(0)
            time.sleep(1)
        
        local_ip = nic.ifconfig()[0]
        print(f'Joined network as {local_ip}!')
        # Turn LED on when connected
        led.value(1)
    
    def mqtt_connect(self):
        self.client = MQTTClient(self.client_id, self.mqtt_uri, user=self.user, password=self.pswd, keepalive=self.keepalive)
        
        # Establish disconnect message
        self.client.set_last_will(self.status_topic, self.disconnect_msg)
        
        try:
            self.client.connect()
        except MQTTException as e:
            print(e)
        else:
            print(f'Connected to MQTT broker @ {self.mqtt_uri}!')
        
        self.client.set_callback(self.callback)
        
        for topic in self.topics:
            print(f'Subscribed to {topic}...')
            self.client.subscribe(topic)
        
        return self.client

    def reconnect(self):
        print('Failed to connect to MQTT broker @ {self.mqtt_uri}. Reconnecting...')
        time.sleep(5)
        machine.reset()
        
    def publish(self, topic, msg):
        self.client.publish(topic, msg)    
        
    def register_buttons(self, buttons):
        self.buttons = buttons
        
        # Register Buttons
        if self.buttons:
            for item in self.buttons:
                pin, handler = item
                button = Pin(pin, Pin.IN, Pin.PULL_UP)
                button.irq(trigger=Pin.IRQ_FALLING, handler=handler)
                
            count = len(self.buttons)
            label = 'button' if count is 1 else 'buttons'
            print('Registered', count, f'{label}...')
        
    def connect(self):
        self.eth_init()

        try:
            self.client = self.mqtt_connect()
        except OSError as e:
            self.reconnect()
        else:
            # Publish connect message
            self.client.publish(self.status_topic, self.connect_msg)
        
    def listen(self):
        print('Listening for messages...')
        while True:
            try:
                self.client.check_msg()
            except OSError as e:
                self.client.reconnect()
                
        self.client.disconnect()
