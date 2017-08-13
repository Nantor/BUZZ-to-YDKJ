import configparser
import evdev
import sys

import time

_file_config = 'buzz.ini'
_default_config = {
    'YDKJ': {
        'player1': 'KEY_Q',
        'player2': 'KEY_B',
        'player3': 'KEY_P',
        'nail': 'KEY_N',
        'answer1': 'KEY_1',
        'answer2': 'KEY_2',
        'answer3': 'KEY_3',
        'answer4': 'KEY_4',
    },
    'general': {
        'nailWithController4': False,

        # only used if 'nailWithController4' is set to False
        'nailDelay': 1000,
        'delay': 500,
    },
    'player1': {
        'buzzer': 'BTN_TRIGGER_HAPPY1',
        'answer1': 'BTN_TRIGGER_HAPPY5',
        'answer2': 'BTN_TRIGGER_HAPPY4',
        'answer3': 'BTN_TRIGGER_HAPPY3',
        'answer4': 'BTN_TRIGGER_HAPPY2',
    },
    'player2': {
        'buzzer': 'BTN_TRIGGER_HAPPY6',
        'answer1': 'BTN_TRIGGER_HAPPY10',
        'answer2': 'BTN_TRIGGER_HAPPY9',
        'answer3': 'BTN_TRIGGER_HAPPY8',
        'answer4': 'BTN_TRIGGER_HAPPY7',
    },
    'player3': {
        'buzzer': 'BTN_TRIGGER_HAPPY11',
        'answer1': 'BTN_TRIGGER_HAPPY15',
        'answer2': 'BTN_TRIGGER_HAPPY14',
        'answer3': 'BTN_TRIGGER_HAPPY13',
        'answer4': 'BTN_TRIGGER_HAPPY12',
    },

    # only used if 'nailWithController4' set to True
    'nailController': {
        'nail': 'BTN_TRIGGER_HAPPY16',
        'player1': 'BTN_TRIGGER_HAPPY20',
        'player2': 'BTN_TRIGGER_HAPPY19',
        'player3': 'BTN_TRIGGER_HAPPY18',
    },
}

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read_dict(_default_config)
    config.read(_file_config)

    rol = 0
    buzz = None
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
