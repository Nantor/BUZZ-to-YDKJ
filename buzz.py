#!/usr/bin/env python3
import ctypes
import json
import math
import threading
import time

import hid
import keyboard

_default_config = {
    'general': {
        'blinking_times': 3,
        'blinking_speed': .1,
    },
    'controller': {
        'vendor_id': 0x054c,
        'product_id': 0x1000,
        '1': 'player1',
        '2': 'player2',
        '3': 'player3',
        '4': 'nail',
    },
    'YDKJ': {
        'player1': 'q',
        'player2': 'b',
        'player3': 'p',
        'nail': 'n',
        'answer1': '1',
        'answer2': '2',
        'answer3': '3',
        'answer4': '4',
    },
}


def _merge_config(original, override):
    if type(override) == type(original):
        if type(original) is dict:
            z = {}
            for k in original:
                z[k] = _merge_config(original[k], override.get(k, None))
            return z
        else:
            return override
    return original


class BuzzControllerMapper(threading.Thread):
    __light_array = [0x00 for _ in range(8)]
    __button_state = None

    def __init__(self, configuration_file='buzz.json'):
        super(BuzzControllerMapper, self).__init__()

        # instantiate stop event
        self._stop_event = threading.Event()

        # instantiate the device class
        if os.path.isfile(configuration_file):
            configuration = _merge_config(_default_config, json.load(open(configuration_file)))
        else:
            configuration = _default_config

        hid.enumerate()
        self._dev = hid.hidapi.hid_open(configuration['controller']['vendor_id'],
                                        configuration['controller']['product_id'], None)
        if self._dev is None:
            info = hid.hidapi.hid_enumerate(configuration['controller']['vendor_id'],
                                            configuration['controller']['product_id'])
            d = info
            while d:
                if d.contents.as_dict()['vendor_id'] == configuration['controller']['vendor_id'] and \
                        d.contents.as_dict()['product_id'] == configuration['controller']['product_id']:
                    self._dev = d
                    break
                d = d.contents.next
            hid.hidapi.hid_free_enumeration(info)

        if self._dev is None:
            raise ValueError('No Device found with vendor_id "{}" and product_id "{}".'.format(
                configuration['controller']['vendor_id'], configuration['controller']['product_id']))

        # set the Buzz controller in none blocking mode
        hid.hidapi.hid_set_nonblocking(self._dev, 1)

        # clear the Buzz controller LEDs
        hid.hidapi.hid_write(self._dev, bytes(self.__light_array), len(self.__light_array))
        data = ctypes.create_string_buffer(5)
        hid.hidapi.hid_read(self._dev, data, 5)
        self.__button_state = data.raw

        # setup Buzz controller mapping
        self._controller_mapping = tuple(configuration['controller'][str(i)] for i in range(1, 5))
        self._player_controller = tuple(
            filter(lambda i: configuration['controller'][str(i + 1)] != 'nail', (i for i in range(4)))
        )
        self._player_controller_button_mapping = ('{!s}', 'answer4', 'answer3', 'answer2', 'answer1')
        self._nail_controller_button_mapping = ('nail', None, 'player3', 'player2', 'player1')

        self._ydkj_buttons = configuration['YDKJ']
        self._blinking_times = configuration['general']['blinking_times']
        self._blinking_speed = configuration['general']['blinking_speed']

    def _light_set(self, controllers, status):
        if self._dev is None:
            raise Exception('Controller closed')
        s = 0xFF if status else 0x00
        for controller in controllers:
            self.__light_array[controller + 2] = s
        hid.hidapi.hid_write(self._dev, bytes(self.__light_array), len(self.__light_array))

    def _blink(self, controllers):
        self._light_set(controllers, True)
        for _ in range(self._blinking_times):
            time.sleep(self._blinking_speed * .3)
            self._light_set(controllers, False)
            time.sleep(self._blinking_speed)
            self._light_set(controllers, True)
        time.sleep(self._blinking_speed * .3)
        self._light_set(controllers, False)

    def _flash(self, controller):
        self._light_set((controller,), True)
        time.sleep(self._blinking_speed * 1.3 * (self._blinking_times + 1))
        self._light_set((controller,), False)

    def _handle_buttons_pressed(self, button):
        controller = int(math.floor(button / 5))
        controller_button = button % 5

        if self._controller_mapping[controller] is not 'nail':
            button_type = self._player_controller_button_mapping[controller_button] \
                .format(self._controller_mapping[controller])
        else:
            button_type = self._nail_controller_button_mapping[controller_button]

        if button_type is not None:
            keyboard.send(self._ydkj_buttons[button_type])

            if button_type in self._controller_mapping:
                if self._controller_mapping[controller] is 'nail':
                    controller = self._controller_mapping.index(button_type)
                flash = threading.Thread(name='Flash-' + str(controller), target=self._flash, args=[controller])
                flash.start()
            if button_type == 'nail':
                blinking = threading.Thread(name='Nailed',
                                            target=self._blink,
                                            args=[self._player_controller])
                blinking.start()

    def _map_controller_buttons(self):
        if self._dev is None:
            raise Exception('Controller closed')
        data = ctypes.create_string_buffer(5)
        size = hid.hidapi.hid_read_timeout(self._dev, data, 5, 1000)
        if size > 0 and data.raw != self.__button_state:
            # red buzzer - controller 1
            if self.__button_state[2] & 0x01 == 0 and data.raw[2] & 0x01 != 0:
                self._handle_buttons_pressed(0)
            # yellow button - controller 1
            if self.__button_state[2] & 0x02 == 0 and data.raw[2] & 0x02 != 0:
                self._handle_buttons_pressed(1)
            # green button - controller 1
            if self.__button_state[2] & 0x04 == 0 and data.raw[2] & 0x04 != 0:
                self._handle_buttons_pressed(2)
            # orange button - controller 1
            if self.__button_state[2] & 0x08 == 0 and data.raw[2] & 0x08 != 0:
                self._handle_buttons_pressed(3)
            # blue button - controller 1
            if self.__button_state[2] & 0x10 == 0 and data.raw[2] & 0x10 != 0:
                self._handle_buttons_pressed(4)

            # red buzzer - controller 2
            if self.__button_state[2] & 0x20 == 0 and data.raw[2] & 0x20 != 0:
                self._handle_buttons_pressed(5)
            # yellow button - controller 2
            if self.__button_state[2] & 0x40 == 0 and data.raw[2] & 0x40 != 0:
                self._handle_buttons_pressed(6)
            # green button - controller 2
            if self.__button_state[2] & 0x80 == 0 and data.raw[2] & 0x80 != 0:
                self._handle_buttons_pressed(7)
            # orange button - controller 2
            if self.__button_state[3] & 0x01 == 0 and data.raw[3] & 0x01 != 0:
                self._handle_buttons_pressed(8)
            # blue button - controller 2
            if self.__button_state[3] & 0x02 == 0 and data.raw[3] & 0x02 != 0:
                self._handle_buttons_pressed(9)

            # red buzzer - controller 3
            if self.__button_state[3] & 0x04 == 0 and data.raw[3] & 0x04 != 0:
                self._handle_buttons_pressed(10)
            # yellow button - controller 3
            if self.__button_state[3] & 0x08 == 0 and data.raw[3] & 0x08 != 0:
                self._handle_buttons_pressed(11)
            # green button - controller 3
            if self.__button_state[3] & 0x10 == 0 and data.raw[3] & 0x10 != 0:
                self._handle_buttons_pressed(12)
            # orange button - controller 3
            if self.__button_state[3] & 0x20 == 0 and data.raw[3] & 0x20 != 0:
                self._handle_buttons_pressed(13)
            # blue button - controller 3
            if self.__button_state[3] & 0x40 == 0 and data.raw[3] & 0x40 != 0:
                self._handle_buttons_pressed(14)

            # red buzzer - controller 4
            if self.__button_state[3] & 0x80 == 0 and data.raw[3] & 0x80 != 0:
                self._handle_buttons_pressed(15)
            # yellow button - controller 4
            if self.__button_state[4] & 0x01 == 0 and data.raw[4] & 0x01 != 0:
                self._handle_buttons_pressed(16)
            # green button - controller 4
            if self.__button_state[4] & 0x02 == 0 and data.raw[4] & 0x02 != 0:
                self._handle_buttons_pressed(17)
            # orange button - controller 4
            if self.__button_state[4] & 0x04 == 0 and data.raw[4] & 0x04 != 0:
                self._handle_buttons_pressed(18)
            # blue button - controller 4
            if self.__button_state[4] & 0x08 == 0 and data.raw[4] & 0x08 != 0:
                self._handle_buttons_pressed(19)

            self.__button_state = data.raw

    def stop(self):
        self._stop_event.set()
        self._dev = None

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        hid.hidapi.hid_set_nonblocking(self._dev, 0)
        while not self.stopped():
            self._map_controller_buttons()
        hid.hidapi.hid_close(self._dev)


if __name__ == '__main__':
    import os
    import stat

    pwd = os.path.realpath(__file__)

    if os.getuid() != 0:
        raise PermissionError('Need to be root for running.')

    pid_file = os.path.join(pwd, 'buzz.pid')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL  # Refer to "man 2 open".
    mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH

    buzz = BuzzControllerMapper(configuration_file=os.path.join(pwd, 'buzz.json'))

    with os.fdopen(os.open(pid_file, flags, mode), 'w') as f:
        f.write(str(os.getpid()))

    buzz.start()

    while buzz.is_alive() and os.path.exists(pid_file):
        time.sleep(1)

    buzz.stop()
    if os.path.exists(pid_file):
        os.remove(pid_file)
    buzz.join(10)
