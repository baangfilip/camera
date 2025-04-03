from gpiozero import LED

led = LED(23)
def led_on():
    led.on()
        
def led_off():
    led.off()