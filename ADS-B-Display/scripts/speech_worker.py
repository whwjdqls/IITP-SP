#!/usr/bin/env python3
"""
speech_worker.py

Records a short chunk of microphone audio, sends it to Google Cloud Speech-to-Text
via REST, and prints the transcript JSON so the C++ app can capture it.
Install deps: pip install sounddevice requests
"""

import argparse
import base64
import json
import os
import queue
import sys
from google import genai

import requests
import sounddevice as sd

GOOGLE_ENDPOINT = "https://speech.googleapis.com/v1/speech:recognize"


def record_audio(sample_rate: int, duration_sec: float) -> bytes:
    """Capture mono PCM audio via the default microphone."""
    q: queue.Queue[bytes] = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(f"Recording warning: {status}", file=sys.stderr)
        q.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=0,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        collected = 0
        target_frames = int(sample_rate * duration_sec)
        chunks: list[bytes] = []
        while collected < target_frames:
            chunk = q.get()
            chunks.append(chunk)
            collected += len(chunk) // 2  # 2 bytes/sample
        return b"".join(chunks)


def build_payload(audio_bytes: bytes, sample_rate: int, language: str, model: str) -> dict:
    """Create the JSON body expected by Google Speech."""
    content = base64.b64encode(audio_bytes).decode("ascii")
    return {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": sample_rate,
            "languageCode": language,
            "model": model,
            "enableAutomaticPunctuation": True,
        },
        "audio": {"content": content},
    }


def call_google_speech(api_key: str, payload: dict) -> dict:
    """POST to Google Speech REST endpoint."""
    url = f"{GOOGLE_ENDPOINT}?key={api_key}"
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def extract_transcript(response_json: dict) -> str:
    """Pull the first transcript string out of the response."""
    results = response_json.get("results", [])
    if not results:
        return ""
    alternatives = results[0].get("alternatives", [])
    if not alternatives:
        return ""
    return alternatives[0].get("transcript", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Speech helper.")
    parser.add_argument("--duration", type=float, default=5.0, help="Recording length in seconds.")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Sample rate Hz.")
    parser.add_argument("--language", default="en-US", help="BCP-47 language code.")
    parser.add_argument("--model", default="latest_long", help="Google Speech model id.")
    parser.add_argument("--api-key", default="AIzaSyCJxDGwkaKdEedfzl1jHkjwEaPFg3T3f5w", help="API key.")
    parser.add_argument("--refinement", action="store_true", help="Enable LLM refinement")

    args = parser.parse_args()

    if not args.api_key:
        print("Provide --api-key or set GOOGLE_SPEECH_API_KEY.", file=sys.stderr)
        sys.exit(1)

    # print("Recording...", file=sys.stderr)
    audio_bytes = record_audio(args.sample_rate, args.duration)
    payload = build_payload(audio_bytes, args.sample_rate, args.language, args.model)

    # print("Calling Google Speech API...", file=sys.stderr)
    response = call_google_speech(args.api_key, payload)
    transcript = extract_transcript(response)

    # print(json.dumps(transcript), ensure_ascii=False))

    if args.refinement:
        client = genai.Client(api_key="AIzaSyBz420tptEuhbGHUyTuQ5Q9_WtzL9cYid0")
        prompt = f"Below text if from the speech, Please refine it well-aligned with the speech {transcript}. Do not add extra text just refine the input text"
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt,
        )
        transcript = str(response.text)
    try:
        # UTF-8로 인코딩해서 stdout.buffer에 직접 쓰기
        sys.stdout.buffer.write(transcript.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
        sys.stdout.buffer.flush()
    except (AttributeError, UnicodeEncodeError):
        # sys.stdout.buffer가 없거나 인코딩 실패 시 대체 방법
        # 문제가 있는 문자를 제거하거나 치환
        safe_text = transcript.encode('ascii', errors='replace').decode('ascii')
        print(safe_text, flush=True)

if __name__ == "__main__":
    main()
