import subprocess
import sys
from pathlib import Path


def burn_subtitles(video_path, subtitle_path, output_path, hard_burn=True):
   
    video_path = Path(video_path)
    subtitle_path = Path(subtitle_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if not subtitle_path.exists():
        raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if hard_burn:
        # Hard burn
        subtitle_path_escaped = str(subtitle_path).replace('\\', '/').replace(':', '\\:')
        
        command = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"subtitles='{subtitle_path_escaped}':force_style='FontSize=24,FontName=Arial,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1'",
            "-c:a", "copy",
            "-y",
            str(output_path)
        ]
    else:
        # Soft subtitles
        command = [
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(subtitle_path),
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-metadata:s:s:0", "language=eng",
            "-y",
            str(output_path)
        ]

    subprocess.run(command, check=True, capture_output=True, text=True)
    
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python subtitle_burner.py <video_path> <subtitle_path> <output_path> [--soft]")
        print("  --soft: Embed as soft subtitles instead of hard burning")
        sys.exit(1)

    hard = "--soft" not in sys.argv
    burn_subtitles(sys.argv[1], sys.argv[2], sys.argv[3], hard_burn=hard)
    print(f"Subtitles {'burned' if hard else 'embedded'} successfully to {sys.argv[3]}")
