# Play YDKJ 🕹 with big red buttons 🔴
Your don't want to play yor favorite game "You don't know Jack" with big bulky keyboard.\
You want to get rid of the trouble, that your best fiend and biggest enemy can interfere with you.\
You are thinking:
>_WTF, I playing a quiz-show, where are the big red button's!_

Than this is your place.

Here you can get a little script, where you can use the playstation 2 _BUZZ_ USB-controller (not bluetooth) with the PC version of the game "You don't know Jack".

## Dependencies
- Python >=3.5
- pip packages: hid, keyboard

## Features
- key mapping of controller buttons to the game keys (done)
- add logic to prevent interfering (done)
- custom configuration (done)
- documentation (WIP)
- use LED's (done)
- other features like: auto run as root, in background and ... (WIP)

## Usage

## Configuration

Default
```json
{
    "YDKJ": {
        "answer1": "1",
        "answer2": "2",
        "answer3": "3",
        "answer4": "4",
        "nail": "n",
        "player1": "q",
        "player2": "b",
        "player3": "p"
    },
    "controller": {
        "1": "player1",
        "2": "player2",
        "3": "player3",
        "4": "nail",
        "product_id": 4096,
        "vendor_id": 1356
    },
    "general": {
        "blinking_speed": 0.1,
        "blinking_times": 3
    }
}
```