#!/usr/bin/env python

import turtle as t

def turtle_from_output():
    t.bgcolor("#344C63")
    t.color("#E39E45")
    t.hideturtle()
    t.pensize(size*2)
    t.speed(0)

    for heading in output:
        t.setheading(-heading*90)
        t.forward(size*4)

    t.mainloop()

def walk():
    global heading
    output.append(heading % 4)

def turn(dir):
    global heading
    heading += dir

def step(size, dir):
    if size != 0:
        turn(-dir)
        step(size-1, -dir)
        walk()
        turn(dir)
        step(size-1, dir)
        walk()
        step(size-1, dir)
        turn(dir)
        walk()
        step(size-1, -dir)
        turn(-dir)

def step_generalized(size, dir):
    if size != 0:
        turn(a*dir)
        step_generalized(size-1,-dir)
        turn(b*dir)
        walk()
        turn(c*dir)
        step_generalized(size-1,dir)
        turn(d*dir)
        walk()
        turn(e*dir)
        step_generalized(size-1,dir)
        turn(f*dir)
        walk()
        turn(g*dir)
        step_generalized(size-1,-dir)
        turn(h*dir)

def step_local_heading(size, dir, lh):
    if size != 0:
        step_local_heading(size-1,-dir,lh+dir)
        output.append(lh % 4)
        step_local_heading(size-1,dir,lh)
        lh += dir
        output.append(lh % 4)
        step_local_heading(size-1,dir,lh-dir)
        lh += dir
        output.append(lh % 4)
        step_local_heading(size-1,-dir,lh+dir)

def step_fueled(size, need_inner):
    global dir
    if size != 0:
        dir = -dir
        turn(dir)
        step_fueled(size-1,True)
        walk()
        if need_inner:
            step_fueled(size,False)
            walk()
        step_fueled(size-1,True)
        turn(dir)
        dir = -dir

###############################################################################
# ITERATIVE

def hilbert_xy(step):
    x, y = 0, 0
    offset = 1

    for _ in range(size):
        q = step % 4

        match q:
            case 0:
                x, y = y - offset, x - offset
            case 1:
                x, y = x - offset, y + offset
            case 2:
                x, y = x + offset, y + offset
            case 3:
                x, y = -(y - offset), -(x + offset)

        step //= 4
        offset *= 2

    return (x, y)

def steps_from_xy():
    global heading

    for n in range(4**size):
        (x0, y0) = hilbert_xy(n)
        (x1, y1) = hilbert_xy(n+1)

        x = (x1 - x0) // 2
        y = (y1 - y0) // 2

        match x:
            case 1:
                heading = 0
                walk()
            case -1:
                heading = 2
                walk()

        match y:
            case 1:
                heading = 3
                walk()
            case -1:
                heading = 1
                walk()

# ITERATIVE VECTOR

# 0 = right
# 1 = down
# 2 = left
# 3 = up
def hilbert_vector(step):
    d = 0
    while True:
       	d += 1
       	q = step % 4
       	step //= 4

       	if q != 3:
            break

    dir = q + 3

    while d < size:
       	d += 1
       	q = step % 4
       	step //= 4

       	if q == 0:
            dir = 3 - dir
       	if q == 3:
            dir = 1 - dir

    return dir % 4

def hilbert_vector_asm(step):
    d = 0
    dir = 100
    while d < size:
        d += 1
       	q = step % 4
       	step //= 4

       	# dir not set yet
       	if dir == 100:
            # try setting
            if q != 3:
               	dir = q + 3
            # no rotation
            continue

        if q == 0:
            dir = 3 - dir
       	if q == 3:
            dir = 1 - dir

    return dir % 4

def steps_from_vectors():
    global heading
    for n in range(4**size):
        heading = hilbert_vector(n)
        walk()

output = []
size = 3

# a,b,c,d,e,f,g,h = 3,0,1,0,0,1,0,3
# heading = 0
# dir = 1
# step_generalized(size,dir)

# a,b,c,d,e,f,g,h = 1,3,0,1,3,2,1,1
# heading = 3
# dir = 1
# step_generalized(size,dir)

# a,b,c,d,e,f,g,h = 1,1,2,3,1,0,3,1
# heading = 1
# dir = 1
# step_generalized(size,dir)

# a,b,c,d,e,f,g,h = 3,2,3,2,2,3,2,3
# heading = 2
# dir = 1
# step_generalized(size,dir)

# heading = 0
# dir = 1
# step_fueled(size, True)

# heading = 3
# dir = 1
# step_local_heading(size,dir,heading)

steps_from_xy()

# steps_from_vectors()
# for n in output:
#     print(format(n, '#08b'))

turtle_from_output()
