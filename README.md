# Auto Subtitler

Automated video subtitle generation and translation using OpenAI's Whisper and LibreTranslate.

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

**That's it!** Open http://localhost:8080 in your browser.

### Usage

#### Web Interface (Recommended)
1. Open http://localhost:8080
2. Drag and drop your video
3. Select source and target languages
4. Choose Whisper model (Medium recommended)
5. Click "Process Video"
6. Download subtitle files when complete



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


| Model  | Size   | Speed       | Quality       | Use Case          |
|--------|--------|------------|--------------|------------------|
| tiny   | 75 MB  | Very High  | Low          | Quick tests       |
| base   | 145 MB | High       | Moderate     | Fast processing   |
| small  | 470 MB | Moderate   | Good         | Balanced          |
| medium | 1.5 GB | Low        | Very High    | Recommended       |
| large  | 3 GB   | Very Low   | Excellent    | Best quality      |

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Dutch, Polish, Turkish

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
├── input/              # Video input (CLI mode)
├── output/             # Subtitle output
└── docker-compose.yml  # Docker configuration
```

## License

MIT License
