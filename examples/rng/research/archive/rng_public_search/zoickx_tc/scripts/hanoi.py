#!/usr/bin/env python

# count trailing zeroes
# e.g. ctz(0b11001000) = 3
def ctz(x):
    return (x & -x).bit_length() - 1

def blind_step(move):
    # the disk number to be moved
    disk = ctz(move)

    # direction in which the disk will be moved; 0 - RIGHT, 1 - LEFT
    direction = disk % 2

    # the set of pegs betwen the move will happen, directed RIGHT
    match move % 3:
        case 1:
            pegs = (0,1)
        case 2:
            pegs = (2,0)
        case 0:
            pegs = (1,2)

    # if direction is LEFT, reverse the peg set
    if direction == 1:
        pegs = tuple(reversed(pegs))

    print(f"Move: {pegs[0]} -> {pegs[1]}")

def blind_step_arith(move):
    peg_from = (move + 2 - ctz(move) % 2) % 3
    peg_to   = (move + 1 + ctz(move) % 2) % 3
    print(f"Move: {peg_from} -> {peg_to}")

size = 5
for move in range(1,2**size):
    blind_step(move)
