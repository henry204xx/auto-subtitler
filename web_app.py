import os
import sys
from pathlib import Path
from flask import Flask, request, send_file, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from threading import Thread
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.audio_extractor import extract_audio
from services.transcribe import transcribe
from services.translate import translate_srt
from app.config import INPUT_DIR, OUTPUT_DIR, WHISPER_MODEL

app = Flask(__name__, static_folder='static')
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


def process_video_async(job_id, video_path, source_lang, target_lang, model_size):
    """Process video in background thread"""
    try:
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 'Extracting audio...'
        
        # Extract audio
        audio_path = OUTPUT_DIR / f"{Path(video_path).stem}_{job_id}_audio.wav"
        extract_audio(str(video_path), str(audio_path))
        
        jobs[job_id]['progress'] = f'Transcribing with {model_size} model...'
        
        # Transcribe
        srt_path = transcribe(str(audio_path), str(OUTPUT_DIR), model_size=model_size)
        jobs[job_id]['original_srt'] = srt_path
        
        # Translate if needed
        translate_needed = source_lang != target_lang
        if translate_needed:
            jobs[job_id]['progress'] = f'Translating from {source_lang} to {target_lang}...'
            # Get LibreTranslate URL from environment
            from app.config import LIBRETRANSLATE_URL
            translated_path = translate_srt(
                srt_path,
                str(OUTPUT_DIR / f"{Path(video_path).stem}_{job_id}_translated.srt"),
                source_lang,
                target_lang,
                LIBRETRANSLATE_URL
            )
            jobs[job_id]['translated_srt'] = translated_path
        
        # Cleanup
        if audio_path.exists():
            audio_path.unlink()
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['progress'] = 'Done!'
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        print(f"Error processing job {job_id}: {e}")


@app.route('/')
def index():
    """Serve the main page"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Subtitler - Video Translation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 2.5em; text-align: center; }
        .subtitle { text-align: center; color: #666; margin-bottom: 40px; font-size: 1.1em; }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 60px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f8f9ff;
            margin-bottom: 30px;
        }
        .upload-area:hover { border-color: #764ba2; background: #f0f1ff; }
        .upload-area.dragover { border-color: #764ba2; background: #e8e9ff; transform: scale(1.02); }
        .upload-icon { font-size: 4em; margin-bottom: 20px; color: #667eea; }
        .upload-text { font-size: 1.2em; color: #333; margin-bottom: 10px; }
        .upload-hint { color: #999; font-size: 0.9em; }
        input[type="file"] { display: none; }
        .options { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .option-group { display: flex; flex-direction: column; }
        label { font-weight: 600; color: #333; margin-bottom: 8px; font-size: 0.95em; }
        select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        select:focus { outline: none; border-color: #667eea; }
        .model-select { grid-column: 1 / -1; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .status { display: none; padding: 20px; background: #f8f9ff; border-radius: 10px; margin-top: 20px; }
        .status.active { display: block; }
        .status-header { display: flex; align-items: center; margin-bottom: 15px; }
        .status-icon { font-size: 2em; margin-right: 15px; }
        .status-text { flex: 1; }
        .status-title { font-weight: 600; color: #333; font-size: 1.1em; }
        .status-message { color: #666; margin-top: 5px; }
        .progress-bar { width: 100%; height: 8px; background: #e0e0e0; border-radius: 10px; overflow: hidden; margin-top: 15px; }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            transition: width 0.3s ease;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .download-buttons { display: flex; gap: 10px; margin-top: 15px; }
        .download-btn {
            flex: 1;
            padding: 12px;
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .download-btn:hover { background: #667eea; color: white; }
        .error { background: #fff5f5; color: #c53030; padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #c53030; }
        .filename { background: #f0f1ff; padding: 10px 15px; border-radius: 8px; margin-bottom: 20px; color: #333; font-weight: 500; display: none; }
        .filename.active { display: block; }
        @media (max-width: 600px) {
            .options { grid-template-columns: 1fr; }
            .model-select { grid-column: 1; }
            h1 { font-size: 2em; }
            .container { padding: 25px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Auto Subtitler</h1>
        <p class="subtitle">Upload your video and get translated subtitles instantly</p>
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📹</div>
            <div class="upload-text">Click to upload or drag and drop</div>
            <div class="upload-hint">Supports MP4, AVI, MOV, MKV, and more (Max 500MB)</div>
            <input type="file" id="fileInput" accept="video/*">
        </div>
        <div class="filename" id="filename"></div>
        <div class="options">
            <div class="option-group">
                <label for="sourceLang">Source Language</label>
                <select id="sourceLang"><option value="en">English</option></select>
            </div>
            <div class="option-group">
                <label for="targetLang">Target Language</label>
                <select id="targetLang"><option value="es">Spanish</option></select>
            </div>
            <div class="option-group model-select">
                <label for="modelSize">Whisper Model (Accuracy vs Speed)</label>
                <select id="modelSize">
                    <option value="tiny">Tiny - 75MB (Very Fast, Basic Quality)</option>
                    <option value="base">Base - 145MB (Fast, Good Quality)</option>
                    <option value="small">Small - 470MB (Balanced)</option>
                    <option value="medium" selected>Medium - 1.5GB (Recommended, High Quality)</option>
                    <option value="large">Large - 3GB (Best Quality, Slower)</option>
                </select>
            </div>
        </div>
        <button id="processBtn" disabled>Select a video to start</button>
        <div class="status" id="status">
            <div class="status-header">
                <div class="status-icon" id="statusIcon">⏳</div>
                <div class="status-text">
                    <div class="status-title" id="statusTitle">Processing...</div>
                    <div class="status-message" id="statusMessage">Please wait</div>
                </div>
            </div>
            <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width: 0%"></div></div>
            <div class="download-buttons" id="downloadButtons" style="display: none;">
                <button class="download-btn" id="downloadOriginal">📄 Download Original</button>
                <button class="download-btn" id="downloadTranslated">🌐 Download Translated</button>
            </div>
        </div>
        <div class="error" id="error" style="display: none;"></div>
    </div>
    <script>
        let selectedFile = null, currentJobId = null;
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const processBtn = document.getElementById('processBtn');
        const status = document.getElementById('status');
        const statusIcon = document.getElementById('statusIcon');
        const statusTitle = document.getElementById('statusTitle');
        const statusMessage = document.getElementById('statusMessage');
        const progressFill = document.getElementById('progressFill');
        const downloadButtons = document.getElementById('downloadButtons');
        const errorDiv = document.getElementById('error');
        const filenameDiv = document.getElementById('filename');
        const sourceLang = document.getElementById('sourceLang');
        const targetLang = document.getElementById('targetLang');
        const modelSize = document.getElementById('modelSize');
        
        fetch('/api/languages').then(res => res.json()).then(languages => {
            sourceLang.innerHTML = languages.map(lang => `<option value="${lang.code}">${lang.name}</option>`).join('');
            targetLang.innerHTML = languages.map(lang => `<option value="${lang.code}">${lang.name}</option>`).join('');
            sourceLang.value = 'en';
            targetLang.value = 'es';
        });
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
        uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) handleFileSelect(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', (e) => { if (e.target.files.length > 0) handleFileSelect(e.target.files[0]); });
        
        function handleFileSelect(file) {
            selectedFile = file;
            filenameDiv.textContent = `📁 ${file.name} (${formatFileSize(file.size)})`;
            filenameDiv.classList.add('active');
            processBtn.disabled = false;
            processBtn.textContent = 'Process Video';
            errorDiv.style.display = 'none';
            status.classList.remove('active');
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024, sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
        
        processBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            const formData = new FormData();
            formData.append('video', selectedFile);
            formData.append('source_lang', sourceLang.value);
            formData.append('target_lang', targetLang.value);
            formData.append('model_size', modelSize.value);
            processBtn.disabled = true;
            processBtn.textContent = 'Uploading...';
            errorDiv.style.display = 'none';
            status.classList.add('active');
            downloadButtons.style.display = 'none';
            statusIcon.textContent = '⏳';
            statusTitle.textContent = 'Uploading...';
            statusMessage.textContent = 'Please wait while we upload your video';
            progressFill.style.width = '20%';
            try {
                const response = await fetch('/api/upload', { method: 'POST', body: formData });
                const result = await response.json();
                if (!response.ok) throw new Error(result.error || 'Upload failed');
                currentJobId = result.job_id;
                pollStatus();
            } catch (error) {
                showError(error.message);
                processBtn.disabled = false;
                processBtn.textContent = 'Try Again';
                status.classList.remove('active');
            }
        });
        
        function pollStatus() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/status/${currentJobId}`);
                    const job = await response.json();
                    if (job.status === 'processing' || job.status === 'queued') {
                        statusIcon.textContent = '⚙️';
                        statusTitle.textContent = 'Processing...';
                        statusMessage.textContent = job.progress || 'Working on your video';
                        progressFill.style.width = '60%';
                    } else if (job.status === 'completed') {
                        clearInterval(interval);
                        showCompleted(job);
                    } else if (job.status === 'error') {
                        clearInterval(interval);
                        showError(job.error || 'Processing failed');
                        processBtn.disabled = false;
                        processBtn.textContent = 'Try Again';
                    }
                } catch (error) {
                    clearInterval(interval);
                    showError('Failed to check status: ' + error.message);
                }
            }, 2000);
        }
        
        function showCompleted(job) {
            statusIcon.textContent = '✅';
            statusTitle.textContent = 'Completed!';
            statusMessage.textContent = 'Your subtitles are ready to download';
            progressFill.style.width = '100%';
            downloadButtons.style.display = 'flex';
            document.getElementById('downloadOriginal').onclick = () => { window.location.href = `/api/download/${currentJobId}?type=original`; };
            document.getElementById('downloadTranslated').onclick = () => { window.location.href = `/api/download/${currentJobId}?type=translated`; };
            if (job.source_lang === job.target_lang) {
                document.getElementById('downloadTranslated').style.display = 'none';
                document.getElementById('downloadOriginal').textContent = '📄 Download Subtitles';
            }
            processBtn.disabled = false;
            processBtn.textContent = 'Process Another Video';
        }
        
        function showError(message) {
            errorDiv.textContent = '❌ Error: ' + message;
            errorDiv.style.display = 'block';
            status.classList.remove('active');
        }
    </script>
</body>
</html>"""


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
    
    # Validate model size
    if model_size not in ['tiny', 'base', 'small', 'medium', 'large']:
        model_size = WHISPER_MODEL
    
    # Save file with unique ID
    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = INPUT_DIR / f"{job_id}_{filename}"
    file.save(str(file_path))
    
    # Create job
    jobs[job_id] = {
        'status': 'queued',
        'progress': 'Uploaded',
        'filename': filename,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'model_size': model_size
    }
    
    # Start processing in background
    thread = Thread(target=process_video_async, args=(job_id, file_path, source_lang, target_lang, model_size))
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


if __name__ == '__main__':
    # Ensure directories exist
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=8080, debug=True)
