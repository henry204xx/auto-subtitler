import subprocess
import sys
from pathlib import Path


def extract_audio(video_path, output_path, sample_rate=16000, channels=1):
   
    video_path = Path(video_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-ar", str(sample_rate),
        "-ac", str(channels),
        "-y",  
        str(output_path)
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python audio_extractor.py <video_path> <output_path>")
        sys.exit(1)

    extract_audio(sys.argv[1], sys.argv[2])
    print(f"Audio extracted successfully to {sys.argv[2]}")