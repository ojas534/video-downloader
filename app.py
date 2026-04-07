import os
import json
import subprocess
import time
import uuid
import re
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

# Ensure the download directory exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def cleanup_old_files():
    """Deletes files older than 1 hour to prevent server storage from filling up."""
    now = time.time()
    for filename in os.listdir(DOWNLOAD_FOLDER):
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.isfile(filepath) and os.stat(filepath).st_mtime < now - 3600:
            try:
                os.remove(filepath)
            except Exception:
                pass

def secure_filename(filename):
    """Removes special characters to create a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'Please provide a valid URL'}), 400

    try:
        # Run yt-dlp to get JSON data (-j) without downloading playlists
        cmd = ['yt-dlp', '-j', '--no-playlist', url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)

        # Parse available formats (Keeping it beginner-friendly)
        formats = []
        
        # Add an "Auto / Best Quality" option by default
        formats.append({'id': 'bestvideo+bestaudio/best', 'label': 'Best Quality (Auto)'})
        
        for f in info.get('formats', []):
            ext = f.get('ext', '')
            res = f.get('resolution', 'audio')
            format_id = f.get('format_id')
            
            # Filter to show only formats with pre-merged video/audio or pure audio
            has_video = f.get('vcodec') != 'none'
            has_audio = f.get('acodec') != 'none'

            if has_video and has_audio:
                formats.append({'id': format_id, 'label': f'{res} - {ext} (Video + Audio)'})
            elif not has_video and has_audio and ext in ['m4a', 'mp3']:
                formats.append({'id': format_id, 'label': f'Audio Only - {ext}'})

        return jsonify({
            'title': info.get('title', 'Unknown Title'),
            'thumbnail': info.get('thumbnail', ''),
            'formats': formats
        })

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to fetch video info. Ensure the URL is valid.'}), 400

@app.route('/api/download', methods=['GET'])
def download():
    cleanup_old_files() # Run cleanup before a new download

    url = request.args.get('url')
    format_id = request.args.get('format_id')
    title = request.args.get('title', 'video')

    if not url or not format_id:
        return "Missing parameters", 400

    # Generate a safe, unique filename for server processing
    unique_id = str(uuid.uuid4())
    temp_output_template = os.path.join(DOWNLOAD_FOLDER, f"{unique_id}.%(ext)s")

    try:
        # Download the requested format
        cmd = ['yt-dlp', '-f', format_id, '-o', temp_output_template, '--no-playlist', url]
        subprocess.run(cmd, check=True)

        # Find the newly created file (yt-dlp determines the extension automatically)
        downloaded_file = None
        for filename in os.listdir(DOWNLOAD_FOLDER):
            if filename.startswith(unique_id):
                downloaded_file = os.path.join(DOWNLOAD_FOLDER, filename)
                break

        if downloaded_file:
            # Determine the correct extension for the user download
            ext = downloaded_file.split('.')[-1]
            safe_title = secure_filename(title)
            
            # Send file to user
            return send_file(
                downloaded_file, 
                as_attachment=True, 
                download_name=f"{safe_title}.{ext}"
            )
        else:
            return "Failed to locate file after download.", 500

    except subprocess.CalledProcessError:
        return "An error occurred during download.", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)