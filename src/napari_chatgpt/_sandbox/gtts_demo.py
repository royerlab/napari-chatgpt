import os
from time import sleep

import pygame
from gtts import gTTS

tts = gTTS("Hello this is a normal text and i am a python package. lol",
           lang='en', tld='us')

filename = "speech.mp3"
tts.save(filename)
pygame.mixer.init()
pygame.mixer.music.load(filename)
pygame.mixer.music.play()

os.remove(filename)
sleep(13)
