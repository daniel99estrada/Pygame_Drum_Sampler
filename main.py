import pyaudio
import wave

import pygame
from pygame.locals import *
import pygame.freetype
import sys, os

from math import floor


# Initialization of pygame modules
pygame.init()
pygame.font.init()

# Set window name.
pygame.display.set_caption('The Box - Sampler')

# Initialization of Fonts
pad_font = pygame.freetype.SysFont('', 15)
mode_font = pygame.freetype.SysFont('', 20)
instructions_font = pygame.freetype.SysFont('Sans', 15)

# Constats to be used in Pygame.
SIZE = WIDTH, HEIGHT = 400, 450
GRAY = (100,100,100)
GRAY2 = (197, 199, 197)
WHITE = (255,255,255)
RED = (100,0,0)
RED2 = (150,50,0)
BLUE = (0,0,100)
GREEN = (36, 110, 56)

# Constats to draw the pads.
SQUARE_WIDTH = 100
PADDING = SQUARE_WIDTH * 0.07
COLS = 3
ROWS = 3
PADS = COLS * ROWS
X = (WIDTH - ((SQUARE_WIDTH + PADDING) * COLS))/2
Y = HEIGHT * 0.22
SQUARE_LOC = [X, Y]

# Constants to record audio in pyaudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Set screen size.
screen = pygame.display.set_mode(SIZE)
pygame.mixer.pre_init(44100,-16,2,512)
pygame.mixer.set_num_channels(9)

# List containing the current color of each rectangle.
squares = {i: GRAY for i in range(PADS)}

# Draw the pads into the screen.
def draw_pads(color,border=0):
    for i in range(PADS):
        if border == 0:
            color = squares[i]

        x = SQUARE_LOC[0] + (SQUARE_WIDTH+PADDING) * (i % 3)
        y = SQUARE_LOC[1] + (SQUARE_WIDTH+PADDING) * floor(i / 3)
        
        pygame.draw.rect(screen, color, pygame.Rect(x,y, SQUARE_WIDTH, SQUARE_WIDTH), border)
        pad_font.render_to(screen, (x + 10, y + 10), str(i+1), WHITE)

def draw_mode_bar(index):
    play_color = [GREEN, GRAY]
    record_color = [GRAY, RED2]

    pygame.draw.rect(screen, GRAY2, pygame.Rect(X,HEIGHT * 0.05, 120, 20))   
    mode_font.render_to(screen, (X , HEIGHT * 0.05), "Play", play_color[index])
    mode_font.render_to(screen, (X+50 , HEIGHT * 0.05), "Record", record_color[index])


instructions = [
    "Trigger samples using your number pad.",
    "Press r to record a new sample.",
    "Select a pad to record to.",
    "Recording..."    
    ]
        
def draw_instructions(mode):
    if mode == "play":
        instructions_font.render_to(screen, (X, HEIGHT * 0.12), instructions[0], GRAY)  
        instructions_font.render_to(screen, (X, HEIGHT * 0.16), instructions[1], GRAY)   

    elif mode == "record":
        instructions_font.render_to(screen, (X, HEIGHT * 0.15), instructions[2], GRAY) 

    else:
        instructions_font.render_to(screen, (X, HEIGHT * 0.15), instructions[3], GRAY) 

# Checks for user input in the form of pygame events.
def check_events(*funcs):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        for func in funcs:
            func(event)


# Loads and sets the volume of a sample.
class Sample():
    def __init__(self,file_name,directory):
        self.note = pygame.mixer.Sound(f'{directory}/{file_name}.wav')
        self.note.set_volume(0.2)

# List of Sound objects with default samples.
samples = [Sample(str(i),"samples") for i in range(9)]

# Dictionary of Sound objects with user recorded samples.
recorded_samples = {}

# askii_map maps pygame.event keys to an index that'll be used to retrieve samples.
askii_map = {K_1: 0, K_2: 1, K_3: 2, K_4: 3, K_5: 4, K_6: 5, K_7: 6, K_8:7, K_9: 8}

def play_mode(event):
    if event.type == KEYDOWN:
        for key, index in (askii_map.items()):
            if event.key == key:
                squares[index] = BLUE
                try:
                    pygame.mixer.Channel(index).play(recorded_samples[index].note)

                except:
                    pygame.mixer.Channel(index).play(samples[index].note)

    if event.type == KEYUP:
        for key, index in (askii_map.items()):
            if event.key == key:
                squares[index] = GRAY

             
def record_mode(event):
    recording = True

    def select_pad(event):
        nonlocal recording
        if event.type == KEYDOWN:
            for key, index in (askii_map.items()):
                if event.key == key:

                    squares[index] = RED
                    screen.fill(WHITE)
                    draw_mode_bar(1)
                    draw_pads(WHITE)
                    draw_instructions("Sampling")
                    draw_pads(color,border=5)
                    pygame.display.update()

                    record(str(index))
                    recorded_samples[index] = Sample(str(index),"recorded")
                    recording = False 

    def exit_mode(event):
        nonlocal recording
        if event.type == KEYDOWN:
            if event.key == K_r:
                recording = False 

    if event.type == KEYDOWN:
        if event.key == K_r:
            counter = 0
            while recording:
                clock.tick(60)

                color = RED
                if counter > 15:
                    color = RED2
                if counter > 30:
                    counter = 0
                counter += 1
                    
                check_events(select_pad, exit_mode)
                screen.fill(WHITE)
                draw_mode_bar(1)
                draw_instructions("record")
                draw_pads(WHITE)
                draw_pads(color,border=5)
                pygame.display.update()


def record(file_name):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    seconds = 2

    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK, exception_on_overflow = False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(f"recorded/{file_name}.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close


clock = pygame.time.Clock()
def main_loop():
    while True:
        clock.tick(60)
        check_events(record_mode,play_mode)
        screen.fill(WHITE)
        draw_mode_bar(0)
        draw_instructions("play")
        draw_pads(GRAY)
        pygame.display.update()

if __name__ == "__main__":
    main_loop()