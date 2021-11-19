import random

MAX_N = MAX_M = 30 
direction_x = [1,0,-1,0]
direction_y = [0,1,0,-1]

def make_route():
    BLOCKS = []
    x, y = 1, 1
    
    for _ in range(random.sample(range(20, 30),1)[0]):
        while True:
            direction = random.sample(range(0,3),1)[0]
            if 0 < x + direction_x[direction] <= MAX_N and 0 < y + direction_y[direction] <= MAX_M:
                x, y = x + direction_x[direction], y + direction_y[direction]
                break
        BLOCKS.append(str(x).zfill(4) + str(y).zfill(4))
    print(BLOCKS)
make_route()