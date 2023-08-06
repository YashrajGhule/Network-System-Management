import os
import sys
import time
import socket
import colorama
import argparse
import threading

class Logger:
    """
    A class that provides logging functionality for the server.
    """
    def __init__(self) -> None:
        colorama.init()
        self.BLUE = colorama.Fore.BLUE
        self.RED = colorama.Fore.RED
        self.YELLOW = colorama.Fore.YELLOW
        self.GREEN = colorama.Fore.GREEN
        self.WHITE = colorama.Fore.WHITE

    def logInfo(self, msg):
        """
        Logs an informational message.

        Args:
        - msg (str): The message to log.
        """
        print(self.BLUE + "[INFO] " + self.WHITE + msg)

    def logError(self, msg):
        """
        Logs an error message.

        Args:
        - msg (str): The message to log.
        """
        print(self.RED + "[ERROR] " + self.WHITE + msg)

    def logWarning(self, msg):
        """
        Logs a warning message.

        Args:
        - msg (str): The message to log.
        """
        print(self.YELLOW + "[WARNING] " + self.WHITE + msg)

    def logSuccess(self, msg):
        """
        Logs a success message.

        Args:
        - msg (str): The message to log.
        """
        print(self.GREEN + "[SUCCESS] " + self.WHITE + msg)

logger = Logger()


class Client:
    """
    A class that represents a client.

    Attributes:
    - client (socket): The socket object used for communication.
    - ip (str): The IP address of the client.
    - port (int): The port number of the client.
    - name (str): The name of the client.
    """

    def __init__(self, client, addr, name) -> None:
        """
        Initializes the Client object.

        Args:
        - client (socket): The socket object used for communication.
        - addr (tuple): A tuple containing the IP address and port number of the client.
        - name (str): The name of the client.
        """
        self.client = client
        self.ip, self.port = addr
        self.name = name

    def send(self, msg: str) -> None:
        """
        Sends a message to the client.

        Args:
        - msg (str): The message to send.
        """
        self.client.send(msg.encode("utf-8"))

    def recv(self) -> str:
        """
        Receives a message from the client.

        Returns:
        - str: The received message.
        """
        return self.client.recv(1024).decode("utf-8")
    
    def close(self) -> None:
        """
        Closes the connection with the client.
        """
        self.client.close()
    
    def clearRecvBuffer(self) -> None:
        """
        Clears the receive buffer.
        """
        try:
            self.client.settimeout(0.01)
            self.client.recv(1024)
            self.client.settimeout(5)
        except:
            self.client.settimeout(5)


class Server:
    """
    A class that represents the server.

    Attributes:
    - host (str): The IP address of the server.
    - port (int): The port number of the server.
    - sock (socket): The socket object used for communication.
    - clients (list): A list of connected clients.
    - Thread (threading.Thread): The thread object used for accepting clients.
    - isServerRunning (bool): A flag indicating whether the server is running.
    - isThreadRunning (bool): A flag indicating whether the thread is running.
    """

    def __init__(self, host, port):
        """
        Initializes the Server object.

        Args:
        - host (str): The IP address of the server.
        - port (int): The port number of the server.
        """
        self.host = host
        self.port = port
        self.clients:list[Client] = []
        self.Thread = threading.Thread(target=self.acceptClients)
        self.isServerRunning = False
        self.isThreadRunning = False

    def startServer(self) -> None:
        """
        Starts the server.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.isServerRunning:
            logger.logError("Server Already Running")
            return
        self.sock.bind((self.host, self.port))
        self.sock.listen(16)
        logger.logInfo("Server started on {}:{}".format(self.host, self.port))
        self.isServerRunning = True
        self.isThreadRunning = True
        self.Thread.start()

    def stopServer(self) -> None:
        """
        Stops the server.
        """
        self.sendToAll("stop")
        if not self.isServerRunning:
            logger.logError("Server Not Running")
            return
        logger.logInfo("Stopping server...")
        self.isServerRunning = False
        self.sock.close()

    def acceptClients(self) -> None:
        """
        Accepts clients.
        THIS FUNCTION SHOULD NOT BE CALLED DIRECTLY.
        """
        logger.logInfo("Waiting for clients...")
        while True:
            try:
                if self.isServerRunning and self.isThreadRunning:
                    client, addr = self.sock.accept()
                    #DISABLED TIMEOUT FOR DEBUGGING
                    #ENABLE FOR PRODUCTION
                    client.settimeout(5)
                    try:
                        name = client.recv(1024).decode("utf-8")
                    except TimeoutError:
                        client.send(b"Request Timed out")
                        client.close()
                        logger.logError("Client timed out with address {}".format(addr))
                        continue
                    except Exception as e:
                        logger.logError(str(e))
                        continue
                    client = Client(client, addr, name)
                    self.clients.append(client)
                    # print("Client {} connected".format(addr))
                    logger.logInfo("\nClient {}{} connected".format(name, addr))
                else:
                    break
            except OSError as e:
                # print("[ERROR] Server Not Running")
                # logger.logError(str(e))
                pass
            except Exception as e:
                # print("[ERROR] {}".format(e))
                logger.logError(e)
        # self.isThreadRunning = False

    def getClientByIp(self, ip) -> Client | None:
        """
        Returns the client object with the specified IP address.

        Args:
        - ip (str): The IP address of the client.

        Returns:
        - Client | None: The client object with the specified IP address, or None if no such client exists.
        """
        self.refreshActiveClients()
        for client in self.clients:
            if client.ip == ip:
                return client
        return None

    def getClientByName(self, name) -> Client | None:
        # Returns the client object with the specified name.

        # Args:
        # - name (str): The name of the client.

        # Returns:
        # - Client | None: The client object with the specified name, or None if no such client exists.
        self.refreshActiveClients()
        for client in self.clients:
            if client.name == name:
                return client
        return None

    def sendToAll(self, msg:str) -> None:
        """
        Sends a message to all connected clients.

        Args:
        - msg (str): The message to send.
        """
        self.refreshActiveClients()
        for client in self.clients:
            client.send(msg)

    def kickIp(self, ip) -> None:
        """
        Kicks the client with the specified IP address from the server.

        Args:
        - ip (str): The IP address of the client to kick.
        """
        self.refreshActiveClients()
        client = self.getClientByIp(ip)
        if client != None:
            client.send("kick")
            client.client.close()
            self.clients.remove(client)

    def refreshActiveClients(self) -> None:
        """
        Refreshes the list of active clients by sending a ping message to each client and removing any that do not respond.
        """
        for client in self.clients:
            try:
                client.send("conntest")
            except:
                self.clients.remove(client)
                logger.logWarning(
                    "Client {} ({}:{}) disconnected".format(client.name, client.ip, client.port)
                )



class ArgumentParser(argparse.ArgumentParser):
    """
    Custom argument parser that prints error messages to stderr instead of stdout.

    Attributes:
    - None
    """

    def error(self, message):
        """
        Prints an error message to stderr.

        Args:
        - message (str): The error message to print.

        Returns:
        - None
        """
        print(f"Error: {message}", file=sys.stderr)
        # self.print_help(sys.stderr)
        pass


class ServerManager:
    def __init__(self, ip, port) -> None:
        self.server = Server(ip, port)
        self.cmds = {
            "start": self.server.startServer,
            "stop": self.server.stopServer,
            "list": self.listClients,
            "stat": self.stat,
            "ping": self.ping,
            "resolve": self.resolve,
            "kick": self.kick,
            "cls": lambda: os.system("cls"),
            "clear": lambda: os.system("cls"),
            "exit": self.exitServer,
            "beep": self.beep,
            "refresh": self.refresh,
            "help": None,
        }

    def cmdExec(self) -> None:
        try:
            parser = ArgumentParser(description="Server Manager",add_help=False)
            parser.add_argument(
                "command",
                type=str.lower,
                help="Command to execute",
                choices=self.cmds.keys(),
            )
            while True:
                cmd = input(colorama.Fore.GREEN + ">>> " + colorama.Fore.WHITE)
                args = parser.parse_known_args(cmd.split())
                if args[0].command == "start":
                    self.cmds[args[0].command]()
                elif args[0].command == "stop":
                    self.cmds[args[0].command]()
                elif args[0].command == "list":
                    self.cmds[args[0].command]()
                elif args[0].command == "stat":
                    self.cmds[args[0].command]()
                elif args[0].command == "ping":
                    self.cmds[args[0].command](args[1])
                elif args[0].command == "resolve":
                    self.cmds[args[0].command](args[1])
                elif args[0].command == "kick":
                    self.cmds[args[0].command](args[1])
                elif args[0].command == "cls" or args[0].command == "clear":
                    self.cmds[args[0].command]()
                elif args[0].command == "exit":
                    self.cmds[args[0].command]()
                elif args[0].command == "beep":
                    self.cmds[args[0].command](args[1])
                elif args[0].command == "refresh":
                    self.cmds[args[0].command]()
                elif args[0].command == "help":
                    parser.print_help()

        except KeyboardInterrupt:
            self.server.stopServer()
        except Exception as e:
            self.server.stopServer()
            logger.logError(str(e))

    def refresh(self):
        self.server.refreshActiveClients()

    def beep(self,cmd):
        parser = ArgumentParser(description="Beep")
        parser.add_argument(
            "-i", "--ip", type=str, help="IP address to beep", default=None
        )
        parser.add_argument(
            "-n", "--name", type=str, help="Name of client to beep", default=None
        )
        parser.add_argument(
            "-a","--all",action="store_true",help="Beep all clients",default=False
        )

    def kick(self, cmd):
        parser = ArgumentParser(description="Kick client")
        parser.add_argument(
            "-i", "--ip", type=str, help="IP address to kick", default=None
        )
        parser.add_argument(
            "-n", "--name", type=str, help="Name of client to kick", default=None
        )
        args = parser.parse_args(cmd)
        if args.ip:
            print("kick ip", args.ip)
        elif args.name:
            print("kick name", args.name)
        else:
            parser.print_help()

    def resolve(self, cmd):
        parser = ArgumentParser(description="Resolve IP address")
        parser.add_argument(
            "-i", "--ip", type=str, help="IP address to resolve", default=None
        )
        parser.add_argument(
            "-n", "--name", type=str, help="Name to resolve", default=None
        )
        args = parser.parse_args(cmd)
        if args.ip:
            client = self.server.getClientByIp(args.ip)
            if client != None:
                print("resolve ip", args.ip, "=>", client.name)
            else:
                print("resolve ip", args.ip, "=>", "None")
        elif args.name:
            client = self.server.getClientByName(args.name)
            if client != None:
                print("resolve name", args.name, "=>", client.ip)
            else:
                print("resolve name", args.name, "=>", "None")
        else:
            parser.print_help()

    def exitServer(self):
        if self.server.isServerRunning:
            self.server.stopServer()
        logger.logInfo("Exiting...")
        exit(0)

    def stat(self):
        print("Server Status")
        print("Server Running:", self.server.isServerRunning)
        print("Thread Running:", self.server.isThreadRunning)
        print("Thread Alive:  ", self.server.Thread.is_alive())
        print("Clients Connected:", len(self.server.clients))
        if self.server.isThreadRunning != self.server.Thread.is_alive():
            self.server.isThreadRunning = self.server.Thread.is_alive()
            logger.logWarning("Thread status mismatch")
            logger.logWarning("Resetting Thread status")
            logger.logWarning("Internal Error might have occured in Server/Thread or there might be a bug in the code")
            logger.logWarning("Please report this issue to the developer")

    def ping(self, cmd):
        parser = ArgumentParser(description="Ping utility")
        parser.add_argument(
            "-a", "--all", action="store_true", help="Ping All Clients", default=False
        )
        parser.add_argument(
            "-i", "--ip", type=str, help="IP address to ping", default=None
        )
        parser.add_argument(
            "-n", "--name", type=str, help="Name of client to ping", default=None
        )

        args = parser.parse_args(cmd)
        if args.all:
            for client in self.server.clients:
                try:
                    print("Pinging", client.name, "["+client.ip+"]")
                    client.send("ping"+" "+str(time.time()))
                    reply = client.recv().split()
                    send_time = round((float(reply[2]) - float(reply[1]))*1000,2)
                    recv_time = round((time.time() - float(reply[2]))*1000,2)
                    print("Server -> Client:", send_time,"ms")
                    print("Client -> Server:", recv_time,"ms")
                    print("Client -> Server -> Client:", send_time + recv_time,"ms\n")
                except:
                    logger.logWarning("Ping failed for client "+client.name)
        elif args.ip:
            client = self.server.getClientByIp(args.ip)
            if client != None:
                try:
                    print("Pinging", client.name, "["+client.ip+"]")
                    client.send("ping"+" "+str(time.time()))
                    reply = client.recv().split()
                    send_time = round((float(reply[2]) - float(reply[1]))*1000,2)
                    recv_time = round((time.time() - float(reply[2]))*1000,2)
                    print("Server -> Client:", send_time,"ms")
                    print("Client -> Server:", recv_time,"ms")
                    print("Client -> Server -> Client:", send_time + recv_time,"ms\n")
                except:
                    logger.logWarning("Ping failed for client "+client.name)
            else:
                logger.logWarning("Client not found")
        elif args.name:
            client = self.server.getClientByName(args.name)
            if client != None:
                try:
                    print("Pinging", client.name, "["+client.ip+"]")
                    client.send("ping"+" "+str(time.time()))
                    reply = client.recv().split()
                    send_time = round((float(reply[2]) - float(reply[1]))*1000,2)
                    recv_time = round((time.time() - float(reply[2]))*1000,2)
                    print("Server -> Client:", send_time,"ms")
                    print("Client -> Server:", recv_time,"ms")
                    print("Client -> Server -> Client:", send_time + recv_time,"ms\n")
                except:
                    logger.logWarning("Ping failed for client "+client.name)
            else:
                logger.logWarning("Client not found")

    def listClients(self):
        print("{:32}{:16}{:6}".format("Name", "IP Address", "Port"))
        for client in self.server.clients:
            print("{:32}{:15}{:6}".format(client.name, client.ip, client.port))


if __name__ == "__main__":
    # logger.logWarning("Please support StackOverflow by visiting https://stackoverflow.com/ and asking/answering questions")
    server = ServerManager("127.0.0.1", 8080)
    server.cmdExec()