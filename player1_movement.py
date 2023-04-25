import json
import random
import socket

MAX_X, MIN_X = 400, 0
MAX_Y, MIN_Y = 400, 0
R = 50 / 2
HOST = '127.0.0.1'
PORT = 9999
PLAYER_NUMBER = "0"

pos = {
    'x': 100, 'y': 100,
    'dx': random.random(), 'dy': random.random()
}

dx, dy = random.uniform(0.0, 0.1), random.uniform(0.0, 0.1)

def step(x, y):
    global dx
    global dy
    nx = x + dx
    ny = y + dy
    if nx + R > MAX_X or nx - R < MIN_X:
        dx *= -1
    if ny + R > MAX_Y or ny - R < MIN_Y:
        dy *= -1
    return nx, ny


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f = s.makefile(mode='rwb', buffering=0) # use file API to interact with socket
    f.write(str(s.getsockname()).encode() + b'\n')
    while True:
        data = json.loads(f.readline())
        piece_type, x, y = data[PLAYER_NUMBER]
        print(f'Got {data}')
        nx, ny = step(x, y)
        data.update({
            PLAYER_NUMBER: [piece_type, nx, ny]
        })
        print(f'New data {data}')
        f.write(json.dumps(data).encode() + b'\n')
