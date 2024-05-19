from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

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
    # TODO start playing the song
    return render_template('player.html', filename=filename)

@app.route('/')
@app.route('/browse/<path:subpath>')
def browse(subpath=''):
    base_dir = '/home/pi/apps/piano-led/midi'  # Change this to your folder path
    abs_path = os.path.join(base_dir, subpath)

    if not os.path.exists(abs_path):
        return redirect(url_for('browse'))

    directories, files = list_files(abs_path)
    return render_template('index.html', directories=directories, files=files, current_path=subpath)


@app.route('/player/<path:action>')
def player(action):
    #switch for action
    match action: 
        case 'speed': 
            # get params from request
            speed = request.args.get('speed')
            print("speed ", speed)
        case 'mute': 
            # get params from request
            mute = request.args.get('mute')
            print("mute ", mute)
        case _:
            print("undefined player action", action)

        
    return ""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')