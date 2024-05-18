from machine import Pin, SPI
import network
import time

LED = Pin(25, Pin.OUT)
MOSI = Pin(19)
MISO = Pin(16)
SCK = Pin (18)
CS = Pin(17)
RESET = Pin(20)

def eth_init():
    spi = SPI(0, 2_000_000, mosi=MOSI, miso=MISO, sck=SCK)
    nic = network.WIZNET5K(spi, CS, RESET)
    nic.active(True)
    while not nic.isconnected():
        time.sleep(1)
        print('Connecting...')
    local_ip = nic.ifconfig()[0]
    print(f'Connected as {local_ip}!')

def main():
    eth_init()
    
    # After init, the LED will blink
    while True:
        LED.value(1)
        time.sleep(0.5)
        LED.value(0)
        time.sleep(0.5)
        
if __name__ == "__main__":
    main()