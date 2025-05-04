from __init__ import entityHandler, client_socket
from server.client import send_to_server

def update_from_server():
    responses = send_to_server(client_socket, entityHandler.player)
    for response in responses:
        if response['msg_type'] == "pos":
            entityHandler.update_server_pos(response["dat"])
        elif response['msg_type'] == "new_client":
            print(f"NEW: {response['dat']}")
        elif response['msg_type'] == "drop_client":
            print(f"DROP: {response['dat']}")
            entityHandler.remove_player(response["dat"]["address"], response["dat"]["port"])