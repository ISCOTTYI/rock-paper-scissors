import json
import time
import random
import requests

MAX_X, MIN_X = 400, 0
MAX_Y, MIN_Y = 400, 0
R = 50 / 2
URL = 'http://localhost:8000'

pos = {
    'x': 100, 'y': 100,
    'dx': random.random(), 'dy': random.random()
}


def step():
    nx = pos['x'] + pos['dx']
    ny = pos['y'] + pos['dy']
    if nx + R > MAX_X or nx - R < MIN_X:
        pos['dx'] *= -1
    if ny + R > MAX_Y or ny - R < MIN_Y:
        pos['dy'] *= -1
    pos['x'] = nx
    pos['y'] = ny


def send():
    d = {
        'x1':  pos['x'],
        'y1':  pos['y'],
        'x2':  pos['x'] + R/2,
        'y2':  pos['y'] + -R/2
    }
    requests.post(URL, json=d)


if __name__ == '__main__':
    while True:
        time.sleep(0.01)
        step()
        send()
