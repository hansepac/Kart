import pygame as pg

class EventHandler():
    def __init__(self):
        pass
        
    def poll_events(self):
        self.events = pg.event.get()

    def keydown(self, key):
        for event in self.events:
            if event.type == pg.KEYDOWN:
                if event.key == key:
                    return True
        return False

    def keyup(self, key):
        for event in self.events:
            if event.type == pg.KEYUP:
                if event.key == key:
                    return True
        return False

    def clicked_any(self) -> bool:
        for event in self.events:
            if event.type == pg.MOUSEBUTTONDOWN:
                return True

    def mousedown(self, mousebutton=1) -> bool:
        for event in self.events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == mousebutton:
                    return True
        return False

    def mouseup(self, mousebutton=1) -> bool:
        for event in self.events:
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == mousebutton:
                    return True
        return False