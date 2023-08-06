import unittest
import threading
import socket
import time
import sys
from io import StringIO
from Server import Server, Client, Logger
import tracemalloc

tracemalloc.start()

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = Server("127.0.0.1", 8080)
        self.server.refreshActiveClients = lambda: None
        self.server.Thread.setDaemon(True)
        self.logger = Logger()
        self.logger.BLUE = ""
        self.logger.GREEN = ""
        self.logger.YELLOW = ""
        self.logger.RED = ""
        self.logger.WHITE = ""

    def test_start_server(self):
        self.server.startServer()
        self.assertTrue(self.server.isServerRunning)

    def test_stop_server(self):
        self.server.startServer()
        self.server.stopServer()
        self.assertFalse(self.server.isServerRunning)

    def test_accept_clients(self):
        self.server.startServer()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 8080))
        self.client.send("test".encode("utf-8"))
        time.sleep(1)
        self.assertEqual(len(self.server.clients), 1)
        self.server.stopServer()

    def test_get_client_by_ip(self):
        self.server.startServer()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 8080))
        self.client.send("test".encode("utf-8"))
        time.sleep(1)
        client = self.server.getClientByIp("127.0.0.1")
        self.assertIsInstance(client, Client)
        self.server.stopServer()

    def test_get_client_by_name(self):
        self.server.startServer()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 8080))
        self.client.send("test".encode("utf-8"))
        time.sleep(1)
        client = self.server.getClientByName("test")
        self.assertIsInstance(client, Client)
        self.server.stopServer()

    def test_send_to_all(self):
        self.server.startServer()
        self.client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client1.connect(("127.0.0.1", 8080))
        self.client1.send("test1".encode("utf-8"))
        self.client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client2.connect(("127.0.0.1", 8080))
        self.client2.send("test2".encode("utf-8"))
        time.sleep(1)
        self.server.sendToAll("test")
        data1 = self.client1.recv(1024).decode("utf-8")
        data2 = self.client2.recv(1024).decode("utf-8")
        self.assertEqual(data1, "test")
        self.assertEqual(data2, "test")
        self.server.stopServer()

    def test_kick_ip(self):
        self.server.startServer()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 8080))
        self.client.send("test".encode("utf-8"))
        time.sleep(1)
        self.server.kickIp("127.0.0.1")
        self.assertEqual(len(self.server.clients), 0)
        self.server.stopServer()

    def test_refresh_active_clients(self):
        self.server.startServer()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 8080))
        self.client.send("test".encode("utf-8"))
        time.sleep(1)
        self.server.refreshActiveClients()
        self.assertEqual(len(self.server.clients), 1)
        self.server.stopServer()

    def test_logger(self):
        capturedOutput = StringIO()
        sys.stdout = capturedOutput
        self.logger.logInfo("test")
        self.assertEqual(capturedOutput.getvalue().strip(), "[INFO] test")
        self.logger.logWarning("test")
        self.assertEqual(capturedOutput.getvalue().strip(), "[INFO] test\n[WARNING] test")
        self.logger.logError("test")
        self.assertEqual(capturedOutput.getvalue().strip(), "[INFO] test\n[WARNING] test\n[ERROR] test")
        self.logger.logSuccess("test")
        self.assertEqual(capturedOutput.getvalue().strip(), "[INFO] test\n[WARNING] test\n[ERROR] test\n[SUCCESS] test")
        sys.stdout = sys.__stdout__

if __name__ == "__main__":
    unittest.main()
