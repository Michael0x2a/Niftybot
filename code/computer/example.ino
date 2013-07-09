/**
 * Turns on an LED on for one second, then off for one second.
 *
 * This is just an example file.
 */
 
int led = 13;

void setup() {
    pinMode(led, OUTPUT);
}

void loop() {
    digitalWrite(led, HIGH);
    delay(1000);
    digitalWrite(led, LOW);
    delay(1000);
}
