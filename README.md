# Auto Subtitler

Modern, professional web application for automated video subtitle generation and translation using OpenAI's Whisper and LibreTranslate.

## Features

- **Modern React UI** - Clean, professional interface built with React 18, TypeScript, and Tailwind CSS
- **AI Transcription** - Powered by OpenAI Whisper with multiple model sizes
- **Translation** - Support for 15 languages via LibreTranslate
- **Multiple Output Options**:
  - **Hard-burn Subtitles** - Permanently embed subtitles into video
  - **Soft Subtitles** - Add toggleable subtitle tracks
  - **SRT Files** - Download subtitle files separately
- **Real-time Progress Tracking** - Visual progress indicators for each processing stage
- **Drag & Drop Upload** - Easy video file uploads with validation
- **Docker Support** - One-command deployment with Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose

### Setup

```bash
git clone <repository-url>
cd auto-subtitler
cp .env.example .env
docker-compose up -d --build
```

Open http://localhost:8080 in your browser.

### Usage

#### Web Interface (Recommended)
1. Open http://localhost:8080
2. Drag and drop your video (or click to browse)
3. Select source and target languages
4. Choose Whisper model (Medium recommended)
5. Select subtitle output mode:
   - **Hard Burn**: Permanently embed subtitles (cannot be turned off)
   - **Soft Subtitles**: Embedded as toggleable track (can be turned on/off in video player)
   - **SRT Only**: Generate subtitle files without modifying video
6. Click "Start Processing"
7. Monitor real-time progress
8. Download your files when complete



## Docker Commands

```bash
# Start services
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything (removes cached models)
docker-compose down -v
docker-compose up -d --build
```

## Whisper Models


| Model  | Size   | Speed       | Quality       | Use Case         |
|--------|--------|------------|--------------|------------------|
| tiny   | 75 MB  | Very High  | Low          | Quick tests       |
| base   | 145 MB | High       | Moderate     | Fast processing   |
| small  | 470 MB | Moderate   | Good         | Balanced          |
| medium | 1.5 GB | Low        | Very High    | Recommended       |
| large  | 3 GB   | Very Low   | Excellent    | Best quality      |

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Dutch, Polish, Turkish

## Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React Icons
- **Backend**: Python, Flask, FFmpeg
- **AI/ML**: OpenAI Whisper, LibreTranslate
- **Deployment**: Docker, Docker Compose

## Configuration

Edit `.env` to change defaults:

```env
WHISPER_MODEL=medium    # Model size
SOURCE_LANG=en         # Default source language
TARGET_LANG=es         # Default target language
```

## Local Development (without Docker)

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install FFmpeg (if not installed)
# Ubuntu/Debian: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from ffmpeg.org

# Start LibreTranslate
docker run -d -p 5000:5000 libretranslate/libretranslate:latest

# Run web server
python web_app.py  # Opens on http://localhost:8080

# Or use CLI
python -m app.app input/video.mp4 --translate
```

## Project Structure

```
auto-subtitler/
├── web_app.py          # Flask web server
├── app/                # CLI application
├── services/           # Processing services
├── input/              # Video input 
├── output/             # Subtitle output
└── docker-compose.yml  # Docker configuration
```

## License

MIT License
