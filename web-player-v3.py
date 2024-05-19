from flask import Flask, send_from_directory, render_template, request, redirect, url_for
import os
from piano import colorWipe,  play_song, strip, pause_song, stop_song, set_speed, back_5_seconds
from rpi_ws281x import PixelStrip, Color
import time 

app = Flask(__name__)

filepath = ""
def list_files(directory):
    """List directories and files in the given directory."""
    files = []
    directories = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file():
                files.append(entry.name)
            elif entry.is_dir():
                directories.append(entry.name)
    return directories, files

@app.route('/run/<path:filename>')
def run_method(filename):
    colorWipe(strip, Color(0, 0, 0), 10)
    global filepath
    filepath = filename
    #play_song("midi/" + filename) 

    return render_template('player.html', filename=filename)

@app.route('/serve/<path:filename>')
def serve_file(filename):

    return send_from_directory('midi', filename)

@app.route('/')
@app.route('/browse/<path:subpath>')
def browse(subpath=''):
    base_dir = '/home/pi/apps/piano-led/midi'  # Change this to your folder path
    abs_path = os.path.join(base_dir, subpath)
    stop_song() 

    if not os.path.exists(abs_path):
        return redirect(url_for('browse'))

    directories, files = list_files(abs_path)
    return render_template('index.html', directories=directories, files=files, current_path=subpath)


@app.route('/player/<path:action>')
def player(action):
    global filepath
    
    #switch for action
    match action: 
        case 'play': 
            play_song("midi/" + filepath) 
        case 'speed': 
            # get params from request
            speed = request.args.get('speed')
            set_speed(speed)
            print("speed ", speed)
        case 'mute': 
            # get params from request
            mute = request.args.get('mute')
            print("mute ", mute)
        case 'back':
            back_5_seconds()
        case 'restart': 
            stop_song() 
            time.sleep(1)
            play_song("midi/" + filepath)
        #case 'stop': 
        #    stop_song()
        case 'pause': 
            pause_song() 
        case _:
            print("undefined player action", action)

        
    return ""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')