void setup() {
  Serial.begin(9600);  // Start the serial communication
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  Serial.println("Hello, world!");  // Print "Hello, world!" to the Serial Monitor
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);
}
