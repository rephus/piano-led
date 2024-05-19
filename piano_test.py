#!/usr/bin/python

import time
from rpi_ws281x import PixelStrip, Color
import argparse
from mido import MidiFile
import RPi.GPIO as GPIO

#GPIO SETUP
microphone = 17
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(microphone, GPIO.IN)

# LED strip configuration:
LED_COUNT = 160        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


FIRST_NOTE_LED = 20 # the first note that will be played on the LED
SONG_SPEED = 0.3 # speed of the song to play 
TIME_GAP = 0.1 # time between notes

mid = MidiFile('keyboardcat.mid', clip=True)
#mid = MidiFile('songs/aeris.mid', clip=True)
#import pdb; pdb.set_trace()
#mid = MidiFile('songs/at_zanarkand.mid', clip=True)
#mid = MidiFile('songs/invention1bach60ppm.mid', clip=True)
#mid = MidiFile('songs/himno de la alegria.mid', clip=True)
#mid = MidiFile('songs/greengreens.mid', clip=True)
#mid = MidiFile('songs/darkwrld.mid', clip=True)
#mid = MidiFile('songs/hyrulecastle.mid', clip=True)
#mid = MidiFile('songs/brinstar.mid', clip=True)
#mid = MidiFile('songs/supermario.mid', clip=True)


# TODO track0 is always metadata ?
print("tracks" , (mid.tracks[0]).__dict__)


#print(mid)
# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)
    

def rainbow(strip, wait_seconds=1):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, wheel(
            (int(i * 256 / strip.numPixels()) ) & 255))
    strip.show()
    time.sleep(wait_seconds)

def calculate_led_position(midi_note):
    # LEDs can have a different density that will not match the piano keys
    # we should conver the midi_note into the LED position

    # Mapping for a 160 LED strip
    match midi_note:

        case 60: return 27 # do
        case 61: return 27 +2  # do # 
        case 62: return 27 +4 # re 
        case 63: return 27 +6 # re # 
        case 64: return 27 +8 # mi 
        case 65: return 27 +11 # fa 
        case 66: return 27 +13 # fa #
        case 67: return 27 +15 # sol
        case 68: return 27 +17 # sol #
        case 69: return 27 +19 # la
        case 70: return 27 +21 # la # 
        case 71: return 27 +23 # si 

        # octava central
        case 72: return 52 # do
        case 73: return 52 + 3 # do # 
        case 74: return 52 + 5 # re 
        case 75: return 52 + 7 # re # 
        case 76: return 52 + 9 # mi 
        case 77: return 52 + 12 # fa 
        case 78: return 52 + 14 # fa #
        case 79: return 52 + 16 # sol
        case 80: return 52 + 18 # sol #
        case 81: return 52 + 20 # la
        case 82: return 52 + 22 # la # 
        case 83: return 52 + 24 # si 


        case 84: return 79 # do
        case 85: return 79 +2  # do # 
        case 86: return 79 + 4 # re 
        case 87: return 79 + 6 # re # 
        case 88: return 79 + 8 # mi 
        case 89: return 79 + 11 # fa 
        case 90: return 79 + 13 # fa #
        case 91: return 79 + 15 # sol
        case 92: return 79 + 17 # sol #
        case 93: return 79 + 19 # la
        case 94: return 79 + 21 # la # 
        case 95: return 79 + 23 # si 

        case _: 
            return 1

def calculate_led_color(midi_note):

    # Each note should have a different LED color
    # based on the rainbow distribution (from red (C) to violet (B))
    match midi_note:

        case 60: return Color(255, 0, 0) # do
        case 61: return  Color(255, 0, 0) # do #
        case 62: return Color(254, 153, 0) # re 
        case 63: return Color(254, 153, 0) # re # 
        case 64: return Color(255, 222, 89) # mi  
        case 65: return Color(125,128,88) # fa 
        case 66: return Color(125,128,88) # fa #
        case 67: return Color(94,131,232) # sol
        case 68: return Color(94,131,232)  # sol #
        case 69: return Color(204,108,231)  # la
        case 70: return Color(204,108,231) # la # 
        case 71: return Color(239, 45,139) # si 
        # octava central
        case 72: return Color(255, 0, 0) # do
        case 73: return Color(255, 0, 0) # do #
        case 74: return Color(254, 153, 0) # re 
        case 75: return Color(254, 153, 0) # re # 
        case 76: return Color(255, 222, 89) # mi 
        case 77: return Color(125,128,88) # fa 
        case 78: return Color(125,128,88) # fa #
        case 79: return  Color(94,131,232) # sol
        case 80: return Color(94,131,232)  # sol #
        case 81: return Color(204,108,231)  # la
        case 82: return Color(204,108,231) # la # 
        case 83: return Color(239, 45,139) # si 
        case _: 
            return Color(255, 0,0)

def play_song(): 
    track = mid.tracks[1]
    for msg in track:
        print(msg)

        if msg.time > 0 : 
            time.sleep(((msg.time - TIME_GAP) / SONG_SPEED) / 1000)
        if msg.type == 'note_on' and msg.velocity > 0:
            note = calculate_led_position(msg.note) #- FIRST_NOTE_LED
            color = calculate_led_color(msg.note)

            strip.setPixelColor(note, color)
            strip.show()
        elif msg.type == 'note_off'  or (msg.type == 'note_on' and msg.velocity == 0):
            note = calculate_led_position(msg.note)# - FIRST_NOTE_LED
            strip.setPixelColor(note, Color(0, 0, 0))
            strip.show()
            time.sleep(TIME_GAP) # add a little gap on note off, we want it to blink in case the next note is the same.
        else:
            print("skipping", msg)

def play_song_with_keys(): 
    # This mode is supposed to play the song and wait for a key press to play the next note
    # It is a cool concept, but it is not working as expected
    # Because the microphone is not reliable to detect the key press
    # This could be achieve only with a MIDI input device
    track = mid.tracks[1]
    note_on = False
    for msg in track:
        print(msg)
        if msg.type == 'note_on':
            note = msg.note - FIRST_NOTE_LED
            strip.setPixelColor(note, Color(255, 0, 0))
            strip.show()
            note_on=True
        elif msg.type == 'note_off' and note_on:
            GPIO.wait_for_edge(microphone, GPIO.FALLING, timeout=3000) # detect any sound 

            strip.setPixelColor(note, Color(0, 0, 0))
            strip.show()
            time.sleep(0.1)
            note_on=False
        else:
            print("skipping", msg)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.

    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        print('Starting strip.')
        #colorWipe(strip, Color(255, 0, 0), 10)  # Red wipe
        #rainbow(strip)
        colorWipe(strip, Color(0, 0, 0), 10)

        play_song() 
        #play_song_with_keys()

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
