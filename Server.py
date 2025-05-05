import socket
import json
import threading
import time

def is_connected(sock):
    try:
        data = sock.recv(1, socket.MSG_PEEK)
        return True
    except BlockingIOError:
        return True  # No data, but still connected
    except socket.error:
        return False

class Client:
    def __init__(self, server_host: str = '127.0.0.1', server_port: int = 51234):
        self.buffer =  ""
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_address = self.client_socket.getsockname()

        try:
            self.client_socket.connect((self.server_host, self.server_port))
        except ConnectionRefusedError:
            print("Connection refused. Retrying...")
            self.connect_to_server()

    def discover_hosts(broadcast_port=37020, timeout=3):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', broadcast_port))
        s.settimeout(timeout)

        found_hosts = set()
        print("Scanning for LAN hosts...")

        try:
            while True:
                data, addr = s.recvfrom(1024)
                message = data.decode()
                if message.startswith("HOST_AVAILABLE:"):
                    _, ip, port = message.strip().split(":")
                    found_hosts.add((ip, int(port)))
        except socket.timeout:
            pass  # Stop listening after timeout

        return list(found_hosts)
    
    def connect_to_server(self):
        connect_attempts = 0
        while connect_attempts < 3:
            try:
                # Create a new socket each attempt
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.server_host, self.server_port))
                self.local_address = self.client_socket.getsockname()
                return True
            except ConnectionRefusedError:
                print("Connection refused. Retrying...")
                connect_attempts += 1
                time.sleep(0.5)
        print(f"Failed to connect to server after {connect_attempts} attempts.")
        return False
        
    def send_to_server(self, data, dtype: str = "live_data"):
        message = json.dumps({
            "msg_type": dtype,
            "dat": data
        }) + "\n\n"

        try:
            self.client_socket.send(message.encode('utf-8'))
        except (ConnectionRefusedError, BrokenPipeError, OSError) as e:
            print(f"Send failed: {e}, attempting to reconnect...")
            self.connect_to_server()
            return None

        try:
            server_data_string = self.client_socket.recv(1096).decode('utf-8')
            self.buffer += server_data_string
            json_strings = self.buffer.strip().split('\n\n')

            try:
                json.loads(json_strings[-1])
                self.buffer = ""
            except json.JSONDecodeError:
                self.buffer = json_strings.pop()

            server_data = []
            for json_string in json_strings:
                if json_string:
                    try:
                        server_data.append(json.loads(json_string))
                    except json.JSONDecodeError as e:
                        print(f"JSON Decode Error: {e} -> {json_string}")
            return server_data

        except socket.error as e:
            print(f"Error receiving data from the server: {e}")
            return None


class ClientData:
    def __init__(self):
        self.address: tuple = None
        self.socket: socket.socket = None
        self.live_data: dict = None
        self.game_setup: dict = None

class Server:
    def __init__(self, host: str = '127.0.0.1', port: int = 51234):
        self.HOST = host
        self.PORT = port
        self.clients = []
        self.game_setup = None

    def broadcast_host_info(self, port=51234, broadcast_port=37020):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        message = f"HOST_AVAILABLE:{socket.gethostbyname(socket.gethostname())}:{port}"
        while True:
            s.sendto(message.encode(), ('<broadcast>', broadcast_port))
            time.sleep(1)  # Broadcast every second

    def handle_client(self, client: ClientData):
        """Handle communication with the connected client."""
        print(f"SERVER: New connection from {client.address}")
        self.clients.append(client)
        self.broadcast_new_client(client.address)

        try:
            buffer = ""
            while True:
                data = client.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                messages = buffer.split("\n\n")
                
                # Handle all complete messages
                for msg in messages[:-1]:
                    try:
                        incoming_data = json.loads(msg)
                        # print(f"SERVER: Received message from {client.address}: {incoming_data}")

                        if incoming_data["msg_type"] == "game_setup":
                            # Handle game setup data
                            client.game_setup = incoming_data["dat"]
                            self.game_setup = incoming_data["dat"]
                            print(f"SERVER: Game setup data from {client.address}: {client.game_setup}")
                        elif incoming_data["msg_type"] == "live_data":
                            # Handle live data (player positions)
                            client.live_data = incoming_data["dat"]

                        # Broadcast updated positions to all clients
                        self.broadcast_data(incoming_data["dat"], dtype=incoming_data["msg_type"], sender=client)
                        # process the message (same as before)
                    except json.JSONDecodeError as e:
                        print(f"SERVER: JSON decode error: {e}")

                # Keep last (possibly incomplete) part in buffer
                buffer = messages[-1]

        except Exception as e:
            print(f"SERVER: Error handling client {client.address}: {e}")
        finally:
            # Cleanup
            self.broadcast_drop_client(client.address)
            print(f"SERVER: Connection closed from {client.address}")
            client.socket.close()
            del client

    def broadcast_data(self, data, dtype: str = "live_data", sender: ClientData = None):
        """Send the current positions of all players to all clients."""
        msg = json.dumps({
            "msg_type": dtype,
            "dat": data
        }) + "\n\n"
        
        for client in self.clients:
            try:
                if client != sender:
                    client.socket.send(msg.encode('utf-8'))
                else:
                    client.socket.send((json.dumps({"msg_type": "ack", "dat": "ack"}) + "\n\n").encode('utf-8'))
            except Exception as e:
                print(f"SERVER: Error sending to client: {e}")
                client.socket.close()
                self.clients.remove(client)
    
    def broadcast_new_client(self, address):
        msg = json.dumps({
            "msg_type": "new_client",
            "dat": {
                "address": address[0],
                "port": address[1]
            }
        }) + "\n\n"
        for client in self.clients:
            try:
                client.socket.send(msg.encode('utf-8'))
            except Exception as e:
                print(f"SERVER: Error sending to client: {e}")
                client.socket.close()
                self.clients.remove(client)
                del client

    def broadcast_drop_client(self, address):
        msg = json.dumps({
            "msg_type": "drop_client",
            "dat": {
                "address": address[0],
                "port": address[1]
            }
        }) + "\n\n"
        for client in self.clients:
            try:
                client.socket.send(msg.encode('utf-8'))
            except Exception as e:
                print(f"SERVER: Error sending to client: {e}")
                client.socket.close()
                self.clients.remove(client)
                del client

    def start_server(self):
        """Start the game server and listen for connections."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.HOST, self.PORT))
        server.listen()
        print(f"SERVER: Server started on {self.HOST}:{self.PORT}")

        # Broadcast host info
        threading.Thread(target=self.broadcast_host_info).start()

        while True:
            client_socket, client_address = server.accept()
            new_client = ClientData()
            new_client.address = client_address
            new_client.socket = client_socket
            thread = threading.Thread(target=self.handle_client, args=(new_client, ))
            thread.start()
            print(f"SERVER: Active connections: {threading.active_count() - 1}")
            if len(self.clients) > 1:
                if self.game_setup:
                    print(f"BROADCAST GAME SETUP: {self.game_setup}")
                    self.broadcast_data(self.game_setup, dtype="game_setup")
                else:
                    NameError("Game setup not initialized yet.")

if __name__ == "__main__":
    server = Server()
    server.start_server()
