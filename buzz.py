import configparser
import evdev
import sys

import time

if __name__ == '__main__':
    rol = 0
    buzz = None
    file_config = 'buzz.ini'

    config = configparser.ConfigParser()
    config.read(file_config)

    while buzz is None:
        time.sleep(.1)
        rol = (rol + 1) % 4
        if rol == 0:
            sys.stdout.write('\rsearching for buzz controller ... /')
        elif rol == 1:
            sys.stdout.write('\rsearching for buzz controller ... |')
        elif rol == 2:
            sys.stdout.write('\rsearching for buzz controller ... \\')
        elif rol == 3:
            sys.stdout.write('\rsearching for buzz controller ... -')

        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]

        for device in devices:
            if 'buzz' in device.name.lower():
                buzz = device
                break
        sys.stdout.flush()

    print()
    print('Controller found: ' + buzz.name)

    for event in buzz.read_loop():
        print(event)
