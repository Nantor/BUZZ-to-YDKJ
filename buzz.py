import configparser
import evdev
import sys
import time

from evdev import ecodes


class BuzzLogic:
    def __init__(self, configuration: configparser.ConfigParser):
        self._currentPlayer = None
        self._next_press = 0
        self._uinput = evdev.UInput()
        self._ydkj = configuration['YDKJ']
        self._general = configuration['general']
        self._players = [configuration['player1'], configuration['player2'], configuration['player3']]
        self._resetPlayer = self._next_press
        self._nail = configuration['nailController']
        self._is_nail = False

    def button_press(self, event: evdev.InputEvent):
        if event.type != ecodes.EV_KEY or event.value != 1:
            return

        if self._resetPlayer < event.timestamp():
            self._currentPlayer = -1
            # print('time past')

        if self._currentPlayer < 0:
            # the buzzer are presst
            if event.code == self._players[0].getKeyCode('buzzer'):
                self._press_player_key(event, 0)
            elif event.code == self._players[1].getKeyCode('buzzer'):
                self._press_player_key(event, 1)
            elif event.code == self._players[2].getKeyCode('buzzer'):
                self._press_player_key(event, 2)

        elif self._next_press < event.timestamp():

            if self._is_nail and self._general.getboolean('nailWithController4'):
                if event.code == self._nail.getKeyCode('player1'):
                    self._press_number(event, 1)
                elif event.code == self._nail.getKeyCode('player2'):
                    self._press_number(event, 2)
                elif event.code == self._nail.getKeyCode('player3'):
                    self._press_number(event, 3)

            elif event.code == self._players[self._currentPlayer].getKeyCode('answer1'):
                self._press_number(event, 1)
            elif event.code == self._players[self._currentPlayer].getKeyCode('answer2'):
                self._press_number(event, 2)
            elif event.code == self._players[self._currentPlayer].getKeyCode('answer3'):
                self._press_number(event, 3)
            elif event.code == self._players[self._currentPlayer].getKeyCode('answer4') and not self._is_nail:
                self._press_number(event, 4)

            elif not self._is_nail:
                if self._general.getboolean('nailWithController4'):
                    if event.code == self._nail.getKeyCode('nail'):
                        self._press_nail(event)
                else:
                    if event.code == self._players[self._currentPlayer].getKeyCode('buzzer'):
                        self._press_nail(event)

        self._uinput.syn()

    def _press_player_key(self, event: evdev.InputEvent, player: int):
        self._currentPlayer = player
        self._uinput.write(ecodes.EV_KEY, self._ydkj.getKeyCode('player' + str(player + 1)), 1)
        self._uinput.write(ecodes.EV_KEY, self._ydkj.getKeyCode('player' + str(player + 1)), 0)
        self._next_press = event.timestamp() + self._general.getfloat('delay')
        self._resetPlayer = event.timestamp() + self._general.getfloat('resetDelay')
        # print('player ' + str(player + 1) + ' pressed (first)')

    def _press_number(self, event: evdev.InputEvent, answer: int):
        self._uinput.write(ecodes.EV_KEY, self._ydkj.getKeyCode('answer' + str(answer)), 1)
        self._uinput.write(ecodes.EV_KEY, self._ydkj.getKeyCode('answer' + str(answer)), 0)
        self._next_press = event.timestamp() + self._general.getfloat('delay')
        self._resetPlayer = 0
        self._is_nail = False
        # print('player ' + str(self._currentPlayer + 1) + ' pressed number ' + str(answer))

    def _press_nail(self, event: evdev.InputEvent):
        self._is_nail = True
        self._next_press = event.timestamp() + self._general.getfloat('delay')
        self._resetPlayer = event.timestamp() + self._general.getfloat('resetDelay')
        self._uinput.write(ecodes.EV_KEY, self._ydkj.getKeyCode('nail'), 1)
        self._uinput.write(ecodes.EV_KEY, self._ydkj.getKeyCode('nail'), 0)
        # print('player ' + str(self._currentPlayer + 1) + ' will nail ... ')


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
        'delay': .4,
        'resetDelay': 10,
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
    config = configparser.ConfigParser(converters={'KeyCode': lambda a: ecodes.ecodes[a]})
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

    logic = BuzzLogic(config)

    for e in buzz.read_loop():
        logic.button_press(e)
