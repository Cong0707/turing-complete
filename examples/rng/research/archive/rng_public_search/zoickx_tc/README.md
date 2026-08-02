# [Turing Complete](https://turingcomplete.game/)

What a great game. I just wanted to share some of the cooler stuff I [built](https://www.youtube.com/playlist?list=PLL86cjqdZc_A6_KxfzZdofFsIBv5BvSPx) for the main campaign.

## Some of my proudest achievements

### [Hilbert Curve in 60 bytes of vanilla LEG assembly](https://www.youtube.com/watch?v=-e5m-4Umqn4&t=2719s)

- Non-recursive
- Using relative coordinate systems for each depth
- Establishing quadrants in these using divmod 4
- Establishing movement vector based on smallest (relevant) quadrant
- Rotating vector as necessary to pop from relative to absolute coordinates
- Saving bytes by:
  + using infinite recursion to emulate `for` with the stack pointer
  + employing modular arithmetic to reduce conditionals
  + merging multiple loops into one using an "unnatural" initial value as indicator

``` assembly
#include "leg.lml"
const _ 0
const li i1|i2|add
const uj i1|i2|j
const ucall i1|i2|call
#########################

const step sp
const quad b
const shift c
const dir d

# initial dir - any "unnatural" value
const dir_init 100

label hilbert_loop

	li _ 1 shift
	li _ dir_init dir

	label loop
		div step shift quad
		i2|mod quad 4 quad

		i2|j|neq dir dir_init rotate
			i2|j|eq quad 3 nodir
				# base dir found
				i2|add quad 3 dir
			label nodir
			uj _ _ loopend
		label rotate
		
		# rotate dir
		i1|j|ult 0 quad noflip0
			i1|sub 3 dir dir
		label noflip0
		i2|j|ult quad 3 noflip3
			i1|sub 1 dir dir
		label noflip3

		label loopend
		i2|mul shift 4 shift
	i2|j|neq shift 1*4*4*4 loop

	i2|mod dir 4 io

ucall _ _ hilbert_loop
```

### [Hilbert Curve 80/22 good-faith ASIC](https://www.youtube.com/watch?v=-e5m-4Umqn4&t=6786s)

- An implementation of the algorithm above in wires

![HILBERT](screenshots/HILBERT.png)

### [Single-tick 476/304 DivMod](https://www.youtube.com/watch?v=7jNyBqjRVC4)

- Performing long division

![DIVMOD](screenshots/DIVMOD.png)


### [Tower of Hanoi 121/46 good-faith ASIC](https://www.youtube.com/watch?v=44qcXiEd9Ko&t=3853s)

- Establishing move entirely from move number `n`
- Disk size <- `count_traling_zeroes(n)`
- Peg pair <- `n % 3`
- Move direction <- `disk_size % 2`

![HANOI](screenshots/HANOI.png)

### [The Maze 66/18 good-faith ASIC](https://www.youtube.com/watch?v=Hbwgv0F_5sg&t=5403s)

*I know a 2-gate solution exists, but this still seems cool...*

![MAZE](screenshots/MAZE.png)

It also corresponds to mere 16 bytes of OVERTURE assembly.

``` assembly
# import robot.oml
const left  0
const step  1
const right 2
const chill 3
const actn  4
const pew   5
#########################

# quick actions
const now     mov | fa | out
const observe mov | in | td

step # cache ->c
mov | fa | tc
const step_now  mov | fc | out

right # cache ->e
mov | fa | te
const right_now mov | fe | out

actn # cache ->f
mov | fa | tf
const actn_now  mov | ff | out

label go

  step_now

  left now
  left now

  label search
  right_now
  observe
  go j_z
  actn_now
  search j
```

## ACT1 (OVERTURE instruction set implementation)

- 562/110

![ACT1](screenshots/ACT1.png)

## LEG

- 2342/1398
- Everything is a register
- Conditional calls
- Read-write-able stack pointer

![LEG](screenshots/LEG.png)
