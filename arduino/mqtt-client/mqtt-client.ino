#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>
#include <Adafruit_NeoPixel.h>
#include <SPI.h>
#include <Ethernet.h>
#include <EthernetClient.h>


// Ethernet settings
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
EthernetClient ethClient;

// MQTT broker settings
#define MQTT_SERVER "192.169.1.211" 
#define MQTT_PORT 1883            
#define CLIENT_ID "pico"
#define USERNAME "pico"               
#define PASSWORD "password"

// Neopixel settings
#define LED_PIN PIN_NEOPIXEL
#define LED_COUNT 1

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

#define GREEN strip.Color(0,255,0)
#define YELLOW strip.Color(255,255,0)

// Create an MQTT client instance
Adafruit_MQTT_Client mqtt(&ethClient, MQTT_SERVER, MQTT_PORT, CLIENT_ID, USERNAME, PASSWORD);

// Create an MQTT topic instance
Adafruit_MQTT_Publish pubTopic = Adafruit_MQTT_Publish(&mqtt, "fleet1/feather/status");
Adafruit_MQTT_Subscribe subTopic1 = Adafruit_MQTT_Subscribe(&mqtt, "fleet1/interior/hall/overheadLight");
Adafruit_MQTT_Subscribe subTopic2 = Adafruit_MQTT_Subscribe(&mqtt, "fleet1/interior/hall/counterLight");
Adafruit_MQTT_Subscribe subTopic3 = Adafruit_MQTT_Subscribe(&mqtt, "fleet1/interior/hall/toeLight");

void setup() {
  // Initialize
  initSerial();
  initNeoPixel();
  initEthernet();

  Serial.print(F("Subscribing to "));
  Serial.println(subTopic1.topic);
  mqtt.subscribe(&subTopic1);

  Serial.print(F("Subscribing to "));
  Serial.println(subTopic2.topic);
  mqtt.subscribe(&subTopic2);

  Serial.print(F("Subscribing to "));
  Serial.println(subTopic3.topic);
  mqtt.subscribe(&subTopic3);
}

void loop() { 
  // Check connection
  connectMQTT();

  processIncomingMessages();

  delay(10);
}

void initSerial(){
  // Start the serial communication
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect
  }
}

void initNeoPixel(){
  // Start the NeoPixel strip
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  strip.setPixelColor(0, YELLOW);
  strip.show(); // Update the strip to display the color
}

void setNeoPixel(uint32_t color){
  strip.setPixelColor(0, color);
  strip.show();
}

void initEthernet(){
  // Initialize ethernet
  Serial.print(F("Finding network... "));
  if (Ethernet.begin(mac) == 0) {
    Serial.println(F("Failed to configure Ethernet using DHCP"));
  }
  delay(1000);
  Serial.print(F("joined as "));
  Serial.println(Ethernet.localIP());
}

void connectMQTT() {
  int8_t ret;

  // Stop if already connected
  if (mqtt.connected()) {
    return;
  }

  Serial.print(F("Connecting to MQTT broker... "));

  while ((ret = mqtt.connect()) != 0) { // Connect will return 0 for a successful connection
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println(F("Retrying MQTT connection in 5 seconds..."));
    mqtt.disconnect();
    delay(5000);  // Wait 5 seconds before retrying
  }

  Serial.print(F("connected to "));
  Serial.println(MQTT_SERVER);
  setNeoPixel(GREEN);
  char msg[] = "{\"connected\":1}";
  pubTopic.publish(msg);
}

void processIncomingMessages() {
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(10))) {
    Serial.print(F("Rec'd "));
    Serial.print(subscription->topic);
    Serial.print(F(" -> "));
    
    if (subscription == &subTopic1) {
      Serial.println((char *)subTopic1.lastread);
    }
    if (subscription == &subTopic2) {
      Serial.println((char *)subTopic2.lastread);
    }
    if (subscription == &subTopic3) {
      Serial.println((char *)subTopic3.lastread);
    }
  }
}
