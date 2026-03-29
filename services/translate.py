import requests
import re
import sys
import json
from pathlib import Path


def load_cache(cache_file="translation_cache/cache.json"):
    
    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists() and cache_path.is_file():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache(cache, cache_file="translation_cache/cache.json"):
    """
    Save translation cache to file.

    Args:
        cache: Dictionary containing translations
        cache_file: Path to cache file
    """
    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def translate_text(text, source, target, libretranslate_url, cache):
    """
    Translate text using LibreTranslate API with caching.

    Args:
        text: Text to translate
        source: Source language code
        target: Target language code
        libretranslate_url: URL of LibreTranslate API
        cache: Translation cache dictionary

    Returns:
        Translated text
    """
    if not text.strip():
        return text

    # Check cache 
    cache_key = f"{source}:{target}:{text}"
    if cache_key in cache:
        return cache[cache_key]

    payload = {"q": text, "source": source, "target": target, "format": "text"}
    try:
        response = requests.post(libretranslate_url, json=payload, timeout=10)
        response.raise_for_status()
        translated = response.json()["translatedText"]

        # Save to cache
        cache[cache_key] = translated
        return translated
    except Exception as e:
        print(f"Translation error: {e}. Keeping original text.")
        return text


def parse_srt(content):
    """
    Parse SRT file content into structured blocks.
    """
    blocks = []
    raw_blocks = re.split(r'\n\s*\n', content.strip())

    for block in raw_blocks:
        lines = block.splitlines()
        if len(lines) >= 3:
            index = lines[0].strip()
            timestamp = lines[1].strip()
            text = "\n".join(lines[2:]).strip()

            if index.isdigit() and '-->' in timestamp:
                blocks.append({
                    "index": index,
                    "timestamp": timestamp,
                    "text": text
                })

    return blocks


def translate_srt(input_path, output_path, source_lang, target_lang,
                  libretranslate_url="http://localhost:5000/translate",
                  cache_file="translation_cache/cache.json"):

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load cache
    cache = load_cache(cache_file)

    with open(input_path, 'r', encoding='utf-8') as f:
        blocks = parse_srt(f.read())

    # Translate blocks
    translated_blocks = []
    total = len(blocks)

    for i, block in enumerate(blocks, start=1):
        print(f"Translating block {i}/{total}...", end='\r')

        translated_text = translate_text(
            block["text"],
            source_lang,
            target_lang,
            libretranslate_url,
            cache
        )

        translated_blocks.append(
            f"{block['index']}\n{block['timestamp']}\n{translated_text}\n"
        )

        if i % 10 == 0:
            save_cache(cache, cache_file)

    print()  # New line after progress

    # Final cache save
    save_cache(cache, cache_file)

    # Write translated SRT
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(translated_blocks))

    return str(output_path)


if __name__ == "__main__":
    import os

    if len(sys.argv) < 3:
        print("Usage: python translate.py <input_srt> <output_srt> [source_lang] [target_lang]")
        sys.exit(1)

    input_srt = sys.argv[1]
    output_srt = sys.argv[2]
    source = sys.argv[3] if len(sys.argv) > 3 else os.getenv("SOURCE_LANG", "en")
    target = sys.argv[4] if len(sys.argv) > 4 else os.getenv("TARGET_LANG", "es")
    lt_url = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000/translate")

    result = translate_srt(input_srt, output_srt, source, target, lt_url)
    print(f"Translation completed: {result}")