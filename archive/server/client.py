import socket
import json

buffer = ""

def send_to_server(client_socket, player):
    # Send player position to the server
    position_data = f"{player.entity.pos.x},{player.entity.pos.y}"
    client_socket.send(position_data.encode('utf-8'))
    global buffer

    try:
        server_data_string = client_socket.recv(1096).decode('utf-8')
        buffer += server_data_string
        # Handle jsons sent in the same response
        json_strings = buffer.strip().split('\n\n')

        try:
            json.loads(json_strings[len(json_strings)-1])
            buffer = ""
        except:
            buffer = json_strings.pop()

        server_data = []
        for json_string in json_strings:
            if json_string:  # Check if the string is not empty
                try:
                    server_data.append(json.loads(json_string))
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
                    for json_string in json_strings:
                        print(f"\n\n {buffer} \n\n")

        return server_data
    except socket.error:
        print("Error receiving data from the server.")