#include <Adafruit_TinyUSB.h>
//#include <Adafruit_NeoPixel.h>

//#define NEOPIXEL_PIN 16
//#define NUM_PIXELS 1

//Adafruit_NeoPixel pixels(NUM_PIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  // put your setup code here, to run once:

  Serial.begin(115200);
  while(!Serial) {
    delay(10);
  }
  
  Serial.println("Hello World");

}

void loop() {
  // put your main code here, to run repeatedly:

}
