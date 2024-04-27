#!/usr/bin/python

import time
from rpi_ws281x import PixelStrip, Color
import argparse
from mido import MidiFile

import RPi.GPIO as GPIO
import time

#GPIO SETUP
microphone = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(microphone, GPIO.IN)

# LED strip configuration:
LED_COUNT = 21        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

mid = MidiFile('keyboardcat.mid', clip=True)
#import pdb; pdb.set_trace()

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

def calculate_led_note(midi_note):
    pass



def play_song(): 
    track = mid.tracks[1]
    for msg in track:
        #print(msg)
        speed = 0.5
        gap = 0.1
        if msg.time > 0 : 
            time.sleep((msg.time - gap / speed) / 1000)
        if msg.type == 'note_on':
            note = msg.note - 66
            strip.setPixelColor(note, Color(255, 0, 0))
            strip.show()
        elif msg.type == 'note_off':
            note = msg.note - 66
            strip.setPixelColor(note, Color(0, 0, 0))
            strip.show()
            time.sleep(gap) 
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
            note = msg.note - 66
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
        colorWipe(strip, Color(255, 0, 0), 10)  # Red wipe
        colorWipe(strip, Color(0, 0, 0), 10)
        
        play_song() 
        #play_song_with_keys()

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
