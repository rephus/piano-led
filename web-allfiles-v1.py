from flask import Flask, render_template
import os

app = Flask(__name__)

def list_files(startpath):
    file_paths = []
    for root, dirs, files in os.walk(startpath):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

@app.route('/')
def index():
    folder_path = 'midi'  # Change this to your folder path
    files = list_files(folder_path)
    return render_template('index.html', files=files)

@app.route('/run/<path:filename>')
def run_method(filename):
    # Define what should happen when a file is clicked
    result = f'Running method on {filename}'
    return result

if __name__ == '__main__':
    app.run(debug=True)