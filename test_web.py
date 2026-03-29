#!/usr/bin/env python3
"""
Quick test script for the web interface
Tests that all components are properly configured
"""

import sys
from pathlib import Path

print("=" * 60)
print("  Auto Subtitler - Web Interface Test")
print("=" * 60)
print()

errors = []
warnings = []

# Check Python version
print("✓ Checking Python version...")
if sys.version_info < (3, 8):
    errors.append("Python 3.8+ is required")
else:
    print(f"  Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# Check if required directories exist
print("\n✓ Checking directories...")
input_dir = Path("input")
output_dir = Path("output")

if not input_dir.exists():
    print("  Creating input directory...")
    input_dir.mkdir(exist_ok=True)

if not output_dir.exists():
    print("  Creating output directory...")
    output_dir.mkdir(exist_ok=True)

print("  input/  ✓")
print("  output/  ✓")

# Check if Flask is installed
print("\n✓ Checking dependencies...")
try:
    import flask
    print(f"  Flask {flask.__version__}  ✓")
except ImportError:
    errors.append("Flask is not installed. Run: pip install flask")

try:
    import werkzeug
    print(f"  Werkzeug {werkzeug.__version__}  ✓")
except ImportError:
    errors.append("Werkzeug is not installed. Run: pip install werkzeug")

try:
    import whisper
    print("  Whisper  ✓")
except ImportError:
    warnings.append("Whisper is not installed. Run: pip install -r requirements.txt")

try:
    import ffmpeg
    print("  FFmpeg-python  ✓")
except ImportError:
    warnings.append("FFmpeg-python is not installed. Run: pip install -r requirements.txt")

print("\n✓ Checking files...")
if not Path("web_app.py").exists():
    errors.append("web_app.py not found")
else:
    print("  web_app.py  ✓")

if not Path("app/config.py").exists():
    errors.append("app/config.py not found")
else:
    print("  app/config.py  ✓")

# Print summary
print("\n" + "=" * 60)
if errors:
    print("❌ ERRORS FOUND:")
    for error in errors:
        print(f"  - {error}")
    print()
    sys.exit(1)

if warnings:
    print("⚠️  WARNINGS:")
    for warning in warnings:
        print(f"  - {warning}")
    print()

print("✅ All checks passed!")
print()
print("To start the web server:")
print("  python web_app.py")
print()
print("Then open: http://localhost:8080")
print("=" * 60)
