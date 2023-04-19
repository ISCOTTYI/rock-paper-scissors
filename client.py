import socket
import json

HOST = '127.0.0.1'
PORT = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
f = s.makefile(mode='rwb', buffering=0) # use file API to interact with socket
while True:
  f.write(b'hi\n')
  data = f.readline()
  # calculate_and_send_move()
  print(f'Got {data}')
