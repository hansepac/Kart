from . import title
from . import game
from .update import update
from .draw import draw
from utils.cores import Core, GameCore
from entities import MapMaster

gc = GameCore()

def game_init(c: Core):
    global gc
    # Setup Host
    if c.onlineState == c.onlineState.HOST:
        # Setup Server Connection
        import subprocess
        server_process = subprocess.Popen(["python3", "Server.py"])

        print(f"Server PID: {server_process.pid}")

        # Setup Client
        from Server import Client
        gc.client = Client()

        gc.mapMaster = MapMaster(c.screen, is_server=True)
        gc.mapMaster.setup_game()

        # Get game info and seed from server
        game_json = gc.mapMaster.get_game_setup_json()
        seed_json = gc.mapMaster.terrainDynamicCoordinator.get_seed_json()

        game_setup_json = {
            "game_setup": game_json,
            "seed": seed_json
        }
        
        # Update local mapMaster
        # client.send_to_server(game_setup_json, "game_setup")
    elif c.onlineState == c.onlineState.CLIENT:
        # Setup Client
        
        gc.client = Client()

        gc.mapMaster = MapMaster(screen=c.screen)
        gc.mapMaster.setup_game()
    else:
        gc.mapMaster = MapMaster(screen=c.screen)
        gc.mapMaster.setup_game()
        
    # Add local player
    gc.mapMaster.addLocalPlayer(car_sprite=0)
    # gc.mapMaster.addLocalPlayer(is_controller=True, car_sprite=1)
    return gc