import socket
import json

PLAYER_ID = None

def make_move(game_state):
    # Write your code here
    #        |
    #        |
    #       \ /
    #        v
    pass


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f = s.makefile(mode='rwb', buffering=0) # use file API to interact with socket
    f.write(str(s.getsockname()).encode() + b'\n')
    PLAYER_ID = (f.readline()).decode()[0]
    while True:
        game_state = json.loads(f.readline())
        print(f'got game state {game_state}')
        move = make_move(game_state)
        print(f'moving to {move}')
        f.write(json.dumps(move).encode() + b'\n')
