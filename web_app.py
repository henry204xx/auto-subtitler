import os
import sys
from pathlib import Path
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from threading import Thread
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.audio_extractor import extract_audio
from services.transcribe import transcribe
from services.translate import translate_srt
from services.subtitle_burner import burn_subtitles
from app.config import INPUT_DIR, OUTPUT_DIR, WHISPER_MODEL

app = Flask(__name__, static_folder='frontend/dist', static_url_path='')
CORS(app, origins=['http://localhost:5173', 'http://localhost:8080'])
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = INPUT_DIR

# Store job status
jobs = {}

# Supported languages for LibreTranslate
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "it", "name": "Italian"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ru", "name": "Russian"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "ar", "name": "Arabic"},
    {"code": "hi", "name": "Hindi"},
    {"code": "nl", "name": "Dutch"},
    {"code": "pl", "name": "Polish"},
    {"code": "tr", "name": "Turkish"},
]


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4v'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_video_async(job_id, video_path, source_lang, target_lang, model_size, burn_subs=False, soft_subs=False):
    """Process video in background thread"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 'Extracting audio'
        jobs[job_id]['progress_percent'] = 15
        
        # Extract audio
        audio_path = OUTPUT_DIR / f"{Path(video_path).stem}_{job_id}_audio.wav"
        extract_audio(str(video_path), str(audio_path))
        
        jobs[job_id]['progress'] = f'Transcribing with {model_size} model'
        jobs[job_id]['progress_percent'] = 40
        
        # Transcribe
        srt_path = transcribe(str(audio_path), str(OUTPUT_DIR), model_size=model_size)
        jobs[job_id]['original_srt'] = srt_path
        
        # Translate if needed
        translate_needed = source_lang != target_lang
        final_srt_path = srt_path
        if translate_needed:
            jobs[job_id]['progress'] = f'Translating from {source_lang} to {target_lang}'
            jobs[job_id]['progress_percent'] = 65
            from app.config import LIBRETRANSLATE_URL
            translated_path = translate_srt(
                srt_path,
                str(OUTPUT_DIR / f"{Path(video_path).stem}_{job_id}_translated.srt"),
                source_lang,
                target_lang,
                LIBRETRANSLATE_URL
            )
            jobs[job_id]['translated_srt'] = translated_path
            final_srt_path = translated_path
        else:
            jobs[job_id]['progress_percent'] = 75
        
        # Embed subtitles into video if requested
        if burn_subs or soft_subs:
            embed_type = 'soft' if soft_subs else 'hard'
            jobs[job_id]['progress'] = f'Embedding subtitles into video ({embed_type})'
            jobs[job_id]['progress_percent'] = 90
            output_video_path = OUTPUT_DIR / f"{Path(video_path).stem}_{job_id}_subtitled.mp4"
            burn_subtitles(str(video_path), final_srt_path, str(output_video_path), hard_burn=not soft_subs)
            jobs[job_id]['output_video'] = str(output_video_path)
        
        # Cleanup audio
        if audio_path.exists():
            audio_path.unlink()
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 'Completed'
        jobs[job_id]['progress_percent'] = 100
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['progress_percent'] = 100
        print(f"Error processing job {job_id}: {e}")


@app.route('/')
def index():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from React build"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    return jsonify(SUPPORTED_LANGUAGES)


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start processing"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Supported: MP4, AVI, MOV, MKV, etc.'}), 400
    
    # Get parameters
    source_lang = request.form.get('source_lang', 'en')
    target_lang = request.form.get('target_lang', 'es')
    model_size = request.form.get('model_size', WHISPER_MODEL)
    burn_subs = request.form.get('burn_subtitles', 'false').lower() == 'true'
    soft_subs = request.form.get('soft_subtitles', 'false').lower() == 'true'
    
    # Validate model size
    if model_size not in ['tiny', 'base', 'small', 'medium', 'large']:
        model_size = WHISPER_MODEL
    
    # Validate subtitle options
    if burn_subs and soft_subs:
        return jsonify({'error': 'Cannot enable both hard burn and soft subtitles'}), 400
    
    # Save file with unique ID
    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = INPUT_DIR / f"{job_id}_{filename}"
    file.save(str(file_path))
    
    # Create job
    jobs[job_id] = {
        'status': 'queued',
        'progress': 'Uploaded',
        'progress_percent': 5,
        'filename': filename,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'model_size': model_size,
        'burn_subtitles': burn_subs,
        'soft_subtitles': soft_subs
    }
    
    # Start processing in background
    thread = Thread(target=process_video_async, args=(job_id, file_path, source_lang, target_lang, model_size, burn_subs, soft_subs))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'message': 'Upload successful, processing started'})


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])


@app.route('/api/download/<job_id>', methods=['GET'])
def download_subtitle(job_id):
    """Download subtitle file"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    # Determine which file to download
    file_type = request.args.get('type', 'translated')
    
    if file_type == 'original' and 'original_srt' in job:
        file_path = job['original_srt']
    elif file_type == 'translated' and 'translated_srt' in job:
        file_path = job['translated_srt']
    elif 'original_srt' in job:
        file_path = job['original_srt']
    else:
        return jsonify({'error': 'No subtitle file available'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=Path(file_path).name)


@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available Whisper models"""
    models = [
        {"value": "tiny", "name": "Tiny (75MB - Very Fast)", "size": "75MB"},
        {"value": "base", "name": "Base (145MB - Fast)", "size": "145MB"},
        {"value": "small", "name": "Small (470MB - Balanced)", "size": "470MB"},
        {"value": "medium", "name": "Medium (1.5GB - Recommended)", "size": "1.5GB"},
        {"value": "large", "name": "Large (3GB - Best Quality)", "size": "3GB"},
    ]
    return jsonify(models)


@app.route('/api/download-video/<job_id>', methods=['GET'])
def download_video(job_id):
    """Download video with burned subtitles"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    if 'output_video' not in job:
        return jsonify({'error': 'No video with subtitles available. Enable "Burn subtitles" option.'}), 404
    
    file_path = job['output_video']
    return send_file(file_path, as_attachment=True, download_name=Path(file_path).name)


if __name__ == '__main__':
    # Ensure directories exist
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=8080, debug=True)
