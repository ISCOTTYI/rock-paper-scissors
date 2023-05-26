import json
import random
import socket
import numpy as np

MAX_X, MIN_X = 400, 0
MAX_Y, MIN_Y = 400, 0
R = 10
HOST = '127.0.0.1'
PORT = 9999
PLAYER_ID = None

v = 0.1
phi = random.uniform(0, 2*np.pi)

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f = s.makefile(mode='rwb', buffering=0) # use file API to interact with socket
    f.write(str(s.getsockname()).encode() + b'\n')
    PLAYER_ID = (f.readline()).decode()[0]
    while True:
        data = json.loads(f.readline())
        print(f'Got {data}')
        agents = data[PLAYER_ID]
        round = data["round"]
        moves = []
        for agent in agents:
            id, kind, x, y = agent
            moves.append([id, v, phi])
        response = {"round": round, "moves": moves}
        print(f'Responding {response}')
        f.write(json.dumps(response).encode() + b'\n')
