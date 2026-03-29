import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.audio_extractor import extract_audio
from services.transcribe import transcribe
from services.translate import translate_srt
from app.config import INPUT_DIR, OUTPUT_DIR, WHISPER_MODEL, SOURCE_LANG, TARGET_LANG


def process_video(video_path, translate=False):
    """
    Process a video file to generate subtitles.

    Args:
        video_path: Path to the input video file
        translate: Whether to translate the subtitles

    Returns:
        Path to the generated subtitle file(s)
    """
    video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    print(f"Processing video: {video_path.name}")

    # Step 1: Extract audio
    print("\n[1/3] Extracting audio...")
    audio_path = OUTPUT_DIR / f"{video_path.stem}_audio.wav"
    extract_audio(str(video_path), str(audio_path))
    print(f"Audio extracted to: {audio_path}")

    # Step 2: Transcribe audio
    print(f"\n[2/3] Transcribing audio (model: {WHISPER_MODEL})...")
    srt_path = transcribe(str(audio_path), str(OUTPUT_DIR), model_size=WHISPER_MODEL)
    print(f"Transcription completed: {srt_path}")

    # Step 3: Translate (optional)
    if translate:
        print(f"\n[3/3] Translating subtitles ({SOURCE_LANG} -> {TARGET_LANG})...")
        translated_path = translate_srt(
            srt_path,
            str(OUTPUT_DIR / f"{video_path.stem}_translated.srt"),
            SOURCE_LANG,
            TARGET_LANG
        )
        print(f"Translation completed: {translated_path}")
        return srt_path, translated_path
    else:
        print("\n[3/3] Translation skipped")

    # Cleanup temporary audio file
    if audio_path.exists():
        audio_path.unlink()
        print(f"\nCleaned up temporary audio file")

    return srt_path


def main():
    parser = argparse.ArgumentParser(
        description="Auto Subtitler - Generate subtitles for video files"
    )
    parser.add_argument(
        "video",
        type=str,
        help="Path to video file or video filename in input directory"
    )
    parser.add_argument(
        "--translate",
        "-t",
        action="store_true",
        help="Translate subtitles after transcription"
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=WHISPER_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help=f"Whisper model size (default: {WHISPER_MODEL})"
    )

    args = parser.parse_args()

    # Check if path is absolute or relative to input directory
    video_path = Path(args.video)
    if not video_path.is_absolute():
        video_path = INPUT_DIR / args.video

    try:
        # Update model if specified
        if args.model != WHISPER_MODEL:
            import app.config as config
            config.WHISPER_MODEL = args.model

        result = process_video(video_path, translate=args.translate)

        print("\n" + "="*50)
        print("SUCCESS! Subtitles generated.")
        print("="*50)

        if args.translate:
            print(f"Original: {result[0]}")
            print(f"Translated: {result[1]}")
        else:
            print(f"Output: {result}")

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

