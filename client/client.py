import socket
import json

PLAYER_ID = None
MAX_X, MIN_X = 400, 0
MAX_Y, MIN_Y = 400, 0
R = 10

NICKNAME = "Test"

def make_move(game_state: str) -> str:
    print(type(game_state))
    print(game_state)
    # Write your code here
    #        |
    #        |
    #       \ /
    #        v
    return # move


if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    f = s.makefile(mode='rwb', buffering=0) # use file API to interact with socket
    welcome_msg = str(s.getsockname()) + f"~{NICKNAME}"
    f.write(welcome_msg.encode() + b'\n')
    PLAYER_ID = (f.readline()).decode()[0]
    while True:
        game_state = (f.readline()).decode()
        move = make_move(game_state)
        f.write(json.dumps(move).encode() + b'\n')
