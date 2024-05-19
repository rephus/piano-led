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
pause = False 
stop = False 
back = False 

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
song_speed = 1 # speed of the song to play 
TIME_GAP = 0 # time between notes

#mid = MidiFile('keyboardcat.mid', clip=True)
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
 
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()


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

def midi_to_led_position(midi_note):
    # Base positions for C notes in different octaves
    base_positions = {48: 1, 60: 27, 72: 53, 84: 79, 96: 105, 108: 132 }
    # Offset positions within an octave
    offsets = [0, 2, 4, 6, 8, 11, 13, 15, 17, 19, 21, 23]
    
    # Calculate the base position for the given note
    octave = (midi_note // 12) * 12
    if octave in base_positions:
        base_position = base_positions[octave]
    else:
        # Calculate the base position if it's not explicitly given
        base_position = base_positions[60] + (octave - 60) // 12 * 25
    
    # Calculate the position within the octave
    note_in_octave = midi_note % 12
    
    return base_position + offsets[note_in_octave]


def midi_to_color(midi_note):
    # Color mappings for notes within an octave
    color_mapping = {
        0: Color(255, 0, 0),      # C
        1: Color(255, 0, 0),      # C#
        2: Color(254, 153, 0),    # D
        3: Color(254, 153, 0),    # D#
        4: Color(255, 222, 89),   # E
        5: Color(125, 128, 88),   # F
        6: Color(125, 128, 88),   # F#
        7: Color(94, 131, 232),   # G
        8: Color(94, 131, 232),   # G#
        9: Color(204, 108, 231),  # A
        10: Color(204, 108, 231), # A#
        11: Color(239, 45, 139)   # B
    }
    
    # Get the position within the octave
    note_in_octave = midi_note % 12
    
    return color_mapping[note_in_octave]


def pause_song(): 
    global pause 
    pause = True 

tempo = 500000  # Standard MIDI tempo 120 BPM
def ticks_to_seconds(ticks, tempo, tpq):
    return (tempo / 1_000_000) * (ticks / tpq)

def stop_song(): 
    print("Called stop_song")

    global stop 
    stop = True

def set_speed(speed): 
    global song_speed
    song_speed = float(speed)

def back_5_seconds(): 
    global back
    back = True 


def play_song(midi_path): 
    global pause 
    global tempo 
    global stop
    global song_speed
    global back 

    stop = False 
    if pause: # Resume song if paused
        pause = False 
        return 
    
    pause = False 
    print("Loading midi path", midi_path)
    mid = MidiFile(midi_path, clip=True)
    print('midi_file.ticks_per_beat', mid.ticks_per_beat)
    tpq = mid.ticks_per_beat
    current_elapsed_time = 0

    track = mid.tracks[1]
    msg_index = 0 
    while msg_index < len(track):
        msg = track[msg_index]  
        msg_index += 1          
        if msg.is_meta and msg.type == 'set_tempo':
            tempo = msg.tempo  # Update tempo if there's a set_tempo message

        if back: 
            back = False 
            target_time =5
            accumulated_time = 0

            for i in range(msg_index, -1, -1):
                accumulated_time += ticks_to_seconds(track[i].time, tempo, tpq)
                if accumulated_time >= target_time:
                    print("Back to msg_index", i)
                    colorWipe(strip, Color(0, 0, 0), 10)

                    msg_index = i
                    break

        if stop: 
            stop = False
            colorWipe(strip, Color(0, 0, 0), 10)

            print("Stopping song ", midi_path)
            return 


        while pause: 
            time.sleep(0.1)
             
        print(msg)

        if msg.time > 0 : 
            current_elapsed_time += ticks_to_seconds(msg.time, tempo, tpq)
            time.sleep(ticks_to_seconds(msg.time, tempo, tpq) / song_speed)
            #time.sleep(((msg.time - TIME_GAP) / SONG_SPEED) / 1000)
        if msg.type == 'note_on' and msg.velocity > 0:
            note = midi_to_led_position(msg.note) #- FIRST_NOTE_LED
            color = midi_to_color(msg.note)

            strip.setPixelColor(note, color)
            strip.show()
        elif msg.type == 'note_off'  or (msg.type == 'note_on' and msg.velocity == 0):
            note = midi_to_led_position(msg.note)# - FIRST_NOTE_LED
            strip.setPixelColor(note, Color(0, 0, 0))
            strip.show()
            time.sleep(TIME_GAP) # add a little gap on note off, we want it to blink in case the next note is the same.
        else:
            print("skipping", msg)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.

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
