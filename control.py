# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi
import chip
import ds18b20

# Get the GPIO module here: https://github.com/xtacocorex/CHIP_IO
import CHIP_IO.GPIO as GPIO  # pylint: disable=F0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = '__YOUR_DEVICE_TOKEN__'

# Constants
LED_PIN = 'XIO-P0'

DATA_SENDING_INTERVAL = 60  # secs
DIAG_SENDING_INTERVAL = 90  # secs
POLL_INTERVAL = 0.5  # secs

LOCATIONS = [
    {'lat': 51.500741, 'lng': -0.124626},  # Big Ben, London, United Kingdom
    {'lat': 40.689323, 'lng': -74.044503}  # Statue of Liberty, New York, USA
]


def led_control(value):
    GPIO.output(LED_PIN, value)
    return GPIO.input(LED_PIN)


GPIO.setup(LED_PIN, GPIO.OUT)


def listen_for_events():
    # write your own logic here
    result = random.randint(1, 5)
    if result == 1:
        return 'RING'

    if result == 5:
        return 'BOOM'

    return 'IDLE'


def get_location():
    return random.choice(LOCATIONS)


def sensor_not_connected():
    return 'Sensor not connected'


def main():
    # load w1 modules
    ds18b20.init_w1()

    # Detect DS18B20 temperature sensors.
    ds_sensors = ds18b20.DS18b20.find_all()

    # Put variable declarations here
    # Available types: 'bool', 'numeric', 'string', 'location'
    variables = {
        'Room Temp': {
            'type': 'numeric' if ds_sensors else 'string',
            'bind': ds_sensors[0] if ds_sensors else sensor_not_connected
        },
        'LED On': {
            'type': 'bool',
            'value': False,
            'bind': led_control,
        },
        'CPU Temp': {
            'type': 'numeric',
            'bind': chip.cpu_temp
        },
        'STATUS': {
            'type': 'string',
            'bind': listen_for_events
        },
        'Location': {
            'type': 'location',
            'bind': get_location
        }
    }

    # Put system data declarations here
    diagnostics = {
        'CPU Temp': chip.cpu_temp,
        'IP Address': chip.ip_address,
        'Host': chip.host_name,
        'Operating System': chip.os_name,
        'Client Version:': cloud4rpi.__version__
    }

    device = cloud4rpi.connect(DEVICE_TOKEN)
    device.declare(variables)
    device.declare_diag(diagnostics)

    device.publish_config()

    # adds a 1 second delay to ensure device variables are created
    sleep(1)

    try:
        diag_timer = 0
        data_timer = 0
        while True:
            if data_timer <= 0:
                device.publish_data()
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                device.publish_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL
            sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.error("ERROR! %s %s", error, sys.exc_info()[0])
        sys.exit(1)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
