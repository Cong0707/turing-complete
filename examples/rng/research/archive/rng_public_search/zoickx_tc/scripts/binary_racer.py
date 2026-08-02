#!/usr/bin/env python3

import string
from pynput.keyboard import Key, Controller, Events

controller = Controller()

base = 16
digits = [chr(i) for i in range(48, 58)] + [chr(i) for i in range(97, 123)]

def read_input() -> str:
    buffer = ''
    with Events() as events:
        for event in events:
            if isinstance(event, Events.Press):
                try:
                    if event.key == Key.backspace:
                        buffer = buffer[:-1]
                    elif event.key.char in digits[:base]:
                        buffer += event.key.char
                    else:
                        return buffer
                except:
                    return buffer

def solve(buffer: str) -> None:
    num = int(buffer, base)

    # unpress buttons in-game
    for char in str(buffer):
        if char in string.digits:
            controller.press(char)
            controller.release(char)

    # win level
    binary = list(format(num, '08b'))[-8:] # forced 8 bits
    print(f'\n{buffer} (base {base})\t->\t{num}\t->\t{"".join(binary)}', end='')
    for n, digit in enumerate(binary, start=1):
        if digit == '1':
            controller.press(str(n))
            controller.release(str(n))
    controller.press(Key.space)
    controller.release(Key.space)

while True:
    buffer = read_input()
    solve(buffer)
