import json
import random
import socket
import numpy as np

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

# dx, dy = random.uniform(0.0, 0.1), random.uniform(0.0, 0.1)
v = 0.1
phi = random.uniform(0, 2*np.pi)

def step(x, y):
    global v, phi
    return [v, phi]

# def step(x, y):
#     global dx
#     global dy
#     nx = x + dx
#     ny = y + dy
#     if nx + R > MAX_X or nx - R < MIN_X:
#         dx *= -1
#     if ny + R > MAX_Y or ny - R < MIN_Y:
#         dy *= -1
#     return nx, ny


if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f = s.makefile(mode='rwb', buffering=0) # use file API to interact with socket
    f.write(str(s.getsockname()).encode() + b'\n')
    while True:
        data = json.loads(f.readline())
        print(f'Got {data}')
        agents = data[PLAYER_NUMBER]
        round = data["round"]
        moves = []
        for agent in agents:
            v, phi = step(*agent[1:])
            moves.append([v, phi])
        response = {"round": round, "moves": moves}
        import time
        time.sleep(1)
        print(f'Responding {response}')
        f.write(json.dumps(response).encode() + b'\n')
