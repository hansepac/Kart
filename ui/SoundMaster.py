import pygame as pg

class SoundMaster:
    def __init__(self):
        pg.mixer.init()

        self.idle_sound = pg.mixer.Sound("assets/sounds/car-idle-sound.mp3")
        self.driving_sound = pg.mixer.Sound("assets/sounds/car-driving-sound.mp3")
        self.drifting_hit = pg.mixer.Sound("assets/sounds/drift-sound.mp3")
        self.go_hit = pg.mixer.Sound("assets/sounds/car-go-sound.mp3")

        pg.mixer.music.load("assets/sounds/music3.mp3")
        pg.mixer.music.play(-1)

        self.idle_sound_count = 0
        self.drive_sound_count = 0

        self.drive_sound_is_playing = False
        self.idle_sound_is_playing = False

    def check_runtime_sounds(self):
        if self.idle_sound_count == 0 and self.idle_sound_is_playing:
            self.idle_sound.stop()
            self.idle_sound_is_playing = False
        elif self.idle_sound_count > 0 and not self.idle_sound_is_playing:
            self.idle_sound.play(loops=-1)
            self.idle_sound_is_playing = True

        if self.drive_sound_count == 0 and self.drive_sound_is_playing:
            self.driving_sound.stop()
            self.drive_sound_is_playing = False
        elif self.drive_sound_count > 0 and not self.drive_sound_is_playing:
            self.driving_sound.play(loops=-1)
            self.drive_sound_is_playing = True


        
