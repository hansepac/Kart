import pygame as pg
from utils.states import GameState, OnlineState
from entities.MapMaster import MapMaster
from Server import Client
from input import Controller

class Core:
    screen: pg.Surface
    clock: pg.time.Clock
    gameState: GameState
    onlineState: OnlineState
    events: list
    dt: float
    win_x: int
    win_y: int
    DEV_MODE: bool
    game_running: bool
    controllers: list[Controller]

class GameCore:
    mapMaster: MapMaster
    client: Client

