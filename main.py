from machine import Pin, I2C, reset, RTC, unique_id, Timer, WDT
import time
import ntptime
# import esp32
import uasyncio
import gc
import micropython

from mqtt_handler import MQTTHandler
from leds import *


#####
# Schematic/Notes
######

# GPIO02 = Chan 1
# GPIO04 = Chan 2
# GPIO25 = Chan 3
# GPIO27 = Chan 4

#####
# Watchdog - 120 seconds, need to be larger then loop time below
#####

wdt = WDT(timeout=120000)

#####
# LED stripes
#####

ledcube = LedGlobe46(12,13,14,15)

#####
# Housekeeping
#####

wdt.feed()
count = 1
errcount = 0

def get_count():
    global count
    return count

def get_errcount():
    global errcount
    return errcount

#####
# MQTT setup
#####

# time to connect WLAN, if marginal reception
time.sleep(5)

sc = MQTTHandler(b'pentling/annikalampi', '192.168.0.13')

#####
# Task definition
#####

async def housekeeping():
    global errcount
    global count
    await uasyncio.sleep_ms(1000)

    while True:
        print("housekeeping() - count {0}, errcount {1}".format(count,errcount))
        wdt.feed()
        gc.collect()
        micropython.mem_info()

        # Too many errors, e.g. could not connect to MQTT
        if errcount > 20:
            reset()

        count += 1
        await uasyncio.sleep_ms(60000)

async def handle_mqtt_tx():
    global errcount
    while True:
        if sc.isconnected():
            print("handle_mqtt_tx() - connected, do publish")
            sc.publish_all()
            await uasyncio.sleep_ms(58000)
        else:
            print("handle_mqtt_tx() - MQTT not connected - try to reconnect")
            sc.connect()
            errcount += 1
            await uasyncio.sleep_ms(18000)

        await uasyncio.sleep_ms(2000)

async def handle_mqtt_rx():
    global errcount
    while True:
        if sc.isconnected():
            print("handle_mqtt_rx() - connected, wait for msg")
            sc.mqtt.wait_msg()

        # errcount += 1

        await uasyncio.sleep_ms(1000)

####
# Main
####

print("main")
main_loop = uasyncio.get_event_loop()

main_loop.create_task(housekeeping())
main_loop.create_task(handle_mqtt_tx())
main_loop.create_task(handle_mqtt_rx())

main_loop.run_forever()
main_loop.close()




