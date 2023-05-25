# Fleet 1 Library

Basic MQTT client stuff for W5100S-EVB-Pico boards and a pinch of opinions.

## Features
- [x] Auto-initialize W5100S-EVB-Pico board ethernet port
- [x] MQTT connect wrapper
- [x] Automatic client-id status topic connect/disconnect messages
- [x] Easily subscribe to a list of topics
- [x] Easily register a list of buttons

## Usage
Assuming `fleet1.py` and `mqtt.py` are on the device in `/lib`:

```
from fleet1 import Fleet1Client

client = Fleet1Client(MY_CLIENT_ID, user=MY_USER, password=MY_PASSWORD, topics=MY_TOPICS, callback=MY_CALLBACK)
client.connect()

# Do anything with the client prior to running the listen loop
# client.register_buttons(MY_BUTTONS) # OPTIONAL EXAMPLE

client.listen()
```

## Docs

### `Fleet1Client` Class
- Hardcoded `mqtt_uri` (you will need to update to your mqtt broker address)
- Generates `status_topic` baded on `client_id` ('client_id/status/')
  - Connect message: `{ 'connected': 1}`
  - LWT (disconnect) message: `{ 'connected': 0}`
- Subscribes to multiple topics based on a list of strings (`['topic1/', 'topic2/']`)
- Callback function is triggered everytime a message is recieved on subscribed topic

#### `.connect()` method
Initializes the ethernet port, connects to the MQTT broker, and publishes a connection message

#### `.register_buttons(buttons)` method
Registers button interrupts based on a list of (pin, callback) tuples.

#### `.listen()` method
Starts the infinite loop of listening for messages. Intentionaly seperate from the `connect()` method to allow additional configuration after the client is initialized but before the listening loop starts (e.g. button interrupt registration)

## Todo
- [ ] Add `debounce` utility
- [ ] Add `pwm_fade` utility
- [ ] Create sensor classes and a `sensor_registration` method?
