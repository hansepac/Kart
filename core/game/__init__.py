from .draw import draw
from .update import update

from __init__ import screen

mapMaster = None
client = None

def game_init(onlineState):
    global mapMaster, client
    
    # MapMaster
    from entities import MapMaster

    # Setup Host
    if onlineState == onlineState.HOST:
        # Setup Server Connection
        import subprocess
        server_process = subprocess.Popen(["python3", "Server.py"])

        print(f"Server PID: {server_process.pid}")

        # Setup Client
        from Server import Client
        client = Client()

        mapMaster = MapMaster(screen, is_server=True)
        mapMaster.setup_game()

        # Get game info and seed from server
        game_json = mapMaster.get_game_setup_json()
        seed_json = mapMaster.terrainDynamicCoordinator.get_seed_json()

        game_setup_json = {
            "game_setup": game_json,
            "seed": seed_json
        }
        
        # Update local mapMaster
        # client.send_to_server(game_setup_json, "game_setup")
    elif onlineState == onlineState.CLIENT:
        # Setup Client
        from Server import Client
        client = Client()

        mapMaster = MapMaster(screen=screen)
        mapMaster.setup_game()
    else:
        mapMaster = MapMaster(screen=screen)
        mapMaster.setup_game()
        
    # Add local player
    mapMaster.addLocalPlayer()
    # mapMaster.addLocalPlayer(is_controller=True)
    
    