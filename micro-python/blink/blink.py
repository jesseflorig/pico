from machine import Pin
import time

LED = Pin(25, Pin.OUT)
BLINK_DURATION = 1

def main():
    while True:
        LED.value(1)
        time.sleep(BLINK_DURATION)
        LED.value(0)
        time.sleep(BLINK_DURATION)
        
if __name__ == "__main__":
    main()