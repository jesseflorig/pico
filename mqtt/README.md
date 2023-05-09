# MQTT Pico Projects

Assorted MQTT projects for Pi Pico development.

As of this writing, all projects have been tested on Wiznet's [W5100S-EVB-Pico](https://www.wiznet.io/product-item/w5100s-evb-pico/)

## Features
 - [x] Auto-join network via DHCP
 - [x] Connect to MQTT Server with username and password
 - [x] Publishes connection status on initial connect and disconnect via last will & testament (LWT)
 - [x] Subscribe to one or more topics

## Examples

 - `mqtt_client`: Base MQTT client using onboard LED
 - `mqtt_client_button_led`: Hardware button (toggles LED and publishes LED state) and LED
 - `mqtt_client_button_pwm`[WIP]: Hardware button and pulse-width modulation (PWM) LED (fade-in/out)
 - `mqtt_client_programmable_button_led`: Hardware button (published button press) and LED

## Notes
 - MQTT topics must match exactly (don't forget trailing "/")

## Todo
 - [ ] Improve debounce method (hardware button is not perfect)
