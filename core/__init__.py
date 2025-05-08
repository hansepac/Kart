from . import title
from . import game
from .update import update
from .draw import draw
from utils.cores import Core, GameCore
from entities import MapMaster
from Server import Client

gc = GameCore()

def online_init(c: Core):
    global gc
    # Setup Host
    if c.onlineState == c.onlineState.HOST:
        # Setup Server Connection
        import subprocess
        server_process = subprocess.Popen(["python3", "Server.py"])
        gc.mapMaster = MapMaster(screen=c.screen)

        print(f"Server PID: {server_process.pid}")

        # Setup Client
        gc.client = Client()
    elif c.onlineState == c.onlineState.CLIENT:
        # Setup Client
        gc.client = Client()

        gc.client.connect_to_server()
        gc.mapMaster = MapMaster(screen=c.screen)

    gc.mapMaster.addLocalPlayer()
    return gc

def game_init(c: Core):
    global gc
    # Setup Host
    if c.onlineState == c.onlineState.HOST:
        # Setup Server Connection
        import subprocess
        server_process = subprocess.Popen(["python3", "Server.py"])

        print(f"Server PID: {server_process.pid}")

        # Setup Client
        gc.client = Client()

        gc.mapMaster = MapMaster(c.screen, is_server=True)
        gc.mapMaster.setup_game()

        # Get game info and seed from server
        game_json = gc.mapMaster.get_game_setup_json()
        seed_json = gc.mapMaster.terrainDynamicCoordinator.get_seed_json()

        # Send game info and seed to server
        game_setup_json = {"game_setup": game_json, "seed": seed_json}
        gc.client.send_to_server(game_setup_json, "game_setup")
    elif c.onlineState == c.onlineState.CLIENT:
        # Setup Client
        gc.client = Client()

        gc.client.connect_to_server()

        gc.mapMaster = MapMaster(screen=c.screen)
        gc.mapMaster.setup_game()
    elif c.onlineState == c.onlineState.LOCAL:
        gc.mapMaster = MapMaster(screen=c.screen)
        gc.mapMaster.setup_game()
        
    # Add local player
    gc.mapMaster.addAIPlayer(car_sprite=1)
    gc.mapMaster.addAIPlayer(car_sprite=2)
    gc.mapMaster.addAIPlayer(car_sprite=3)
    for controller in c.controllers:
        gc.mapMaster.addLocalPlayer(controller, car_sprite=0)

    return gc