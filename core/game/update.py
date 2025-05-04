from utils.cores import Core, GameCore

def update(c: Core, gc: GameCore):
    local_game_data = gc.mapMaster.get_game_data()
    server_data = gc.client.send_to_server(local_game_data)
    
    server_game_data = None
    if server_data:
        for response in server_data:
            if response['msg_type'] == "live_data":
                server_game_data = response["dat"]
            elif response['msg_type'] == "game_setup":
                server_game_data = response["dat"]
            elif response['msg_type'] == "new_client":
                print(f"NEW: {response['dat']}")
            elif response['msg_type'] == "drop_client":
                print(f"DROP: {response['dat']}")
            

    if server_game_data:
        gc.mapMaster.update_from_server(server_data)
    gc.mapMaster.update(c)

    return c
