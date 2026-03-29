import whisper
import sys
from pathlib import Path


def transcribe(audio_path, output_dir="output", model_size="medium"):
  
    audio_path = Path(audio_path)
    output_dir = Path(output_dir)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)

    print(f"Transcribing {audio_path.name}...")
    result = model.transcribe(str(audio_path))

    srt_filename = f"{audio_path.stem.replace('_audio', '')}.srt"
    srt_path = output_dir / srt_filename

    with open(srt_path, "w", encoding="utf-8") as f:
        write_srt(result["segments"], f)

    return str(srt_path)


def format_timestamp(seconds):
    """
    Format seconds as SRT timestamp (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds (float)

    Returns:
        Formatted timestamp string
    """
    millisec = int(seconds * 1000)
    hours = millisec // 3600000
    minutes = (millisec % 3600000) // 60000
    secs = (millisec % 60000) // 1000
    milliseconds = millisec % 1000

    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def write_srt(segments, file):
   
    for i, segment in enumerate(segments, start=1):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip()

        file.write(f"{i}\n")
        file.write(f"{start} --> {end}\n")
        file.write(f"{text}\n\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_path> [output_dir] [model_size]")
        sys.exit(1)

    audio = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output"
    model = sys.argv[3] if len(sys.argv) > 3 else "medium"

    srt_path = transcribe(audio, output, model)
    print(f"Transcription saved to: {srt_path}")