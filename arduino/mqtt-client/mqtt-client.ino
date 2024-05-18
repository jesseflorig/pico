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
Adafruit_MQTT_Publish publishTopic = Adafruit_MQTT_Publish(&mqtt, "fleet1/feather/status");
Adafruit_MQTT_Subscribe sub1 = Adafruit_MQTT_Subscribe(&mqtt, "fleet1/interior/hall/test");
Adafruit_MQTT_Subscribe sub2 = Adafruit_MQTT_Subscribe(&mqtt, "fleet1/interior/hall/overheadLight");
Adafruit_MQTT_Subscribe sub3 = Adafruit_MQTT_Subscribe(&mqtt, "fleet1/interior/hall/toeLight");



void setup() {
  // Initialize
  initSerial();
  initNeoPixel();
  initEthernet();

  // Connect to the broker
  connectMQTT();
  
  mqtt.subscribe(&sub1);
  mqtt.subscribe(&sub2);
  mqtt.subscribe(&sub3);
}

void loop() {
  // Ensure the connection to the MQTT broker
  if (!mqtt.connected()) {
    reconnectMQTT();
  }

  processIncomingMessages();

  // Wait before publishing again
  delay(100);
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
  Serial.println(F("Starting Ethernet..."));
  if (Ethernet.begin(mac) == 0) {
    Serial.println(F("Failed to configure Ethernet using DHCP"));
  }
  delay(1000);
  Serial.println(F("Ethernet started"));
}

void connectMQTT() {
  int8_t ret;

  // Stop if already connected
  if (mqtt.connected()) {
    return;
  }

  Serial.print(F("Connecting to MQTT... "));

  while ((ret = mqtt.connect()) != 0) { // Connect will return 0 for a successful connection
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println(F("Retrying MQTT connection in 5 seconds..."));
    mqtt.disconnect();
    delay(5000);  // Wait 5 seconds before retrying
  }

  publishConnectMessage();
}

void reconnectMQTT() {
  while (!mqtt.connected()) {
    Serial.print(F("Connecting to MQTT..."));
    if (mqtt.connect() == 0) {
      publishConnectMessage();
      
    } else {
      Serial.println(mqtt.connectErrorString(mqtt.connect()));
      Serial.println(F("Retrying MQTT connection in 5 seconds..."));
      delay(5000);
    }
  }
}

void publishConnectMessage(){
  Serial.println("MQTT Connected!");
  setNeoPixel(GREEN);
  char msg[] = "{\"connected\":1}";
  publishTopic.publish(msg);
}

void processIncomingMessages() {
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(100))) {
    if (subscription == &sub1) {
      Serial.print(F("Received 1: "));
      Serial.println((char *)sub1.lastread);
    }
    if (subscription == &sub2) {
      Serial.print(F("Received 2: "));
      Serial.println((char *)sub2.lastread);
    }
    if (subscription == &sub3) {
      Serial.print(F("Received 3: "));
      Serial.println((char *)sub3.lastread);
    }
  }
}
