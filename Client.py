import os
import sys
import time
import socket
import threading

#General Configuration
host = "localhost"
port = 8080
buffer_size = 1024
server_address = (host, port)
name = input("Enter Name: ")#os.getlogin()

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(server_address)
        self.client.send(name.encode())

    def send(self, message: str) -> None:
        self.client.send(message.encode())

    def receive(self) -> str:
        data = self.client.recv(buffer_size)
        return data.decode()

    def close(self):
        self.client.close()

class CommandModule:
    def __init__(self):
        self.client = Client()
        self.cmds = {
            "ping": self.ping,
            "beep": self.beep,
        }
        while True:
            cmd = self.client.receive()
            if cmd.startswith("ping"):
                self.ping(cmd)
            if cmd.startswith("stop"):
                break

    # This function has a potential bug as system time may be different on the client and server
    def ping(self,cmd):
        ping_pack = cmd.split(" ")
        ping_pack.append(str(time.time()))
        ping_pack = " ".join(ping_pack)
        self.client.send(ping_pack)

    def beep(self):
        pass

    def close(self):
        self.client.close()

if __name__ == "__main__":
    cmd = CommandModule()
    cmd.close()