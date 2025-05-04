from __init__ import DEBUG
import core.game as game

def update(events, dt, gameState, onlineState):
    local_game_data = game.mapMaster.get_game_data()
    server_data = game.client.send_to_server(local_game_data)
    
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
        game.mapMaster.update_from_server(server_data)
    game.mapMaster.update(events, dt, DEBUG)

    return gameState
