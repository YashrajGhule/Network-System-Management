import socket
import threading
import time

sock = socket.socket()
sock.bind(('localhost',998))

def listen():
    print("Listening...")
    sock.listen(16)
    print(sock.accept())
    
thread = threading.Thread(target=listen)
thread.start()

time.sleep(3)
sock.close()