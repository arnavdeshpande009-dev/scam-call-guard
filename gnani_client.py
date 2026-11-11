"""Gnani AI API client for Prisma (Speech-to-Text) and Timbre (Text-to-Speech).

Handles authentication, timeouts, sequential requests, rate limits (429 retry),
duration limits, and user-friendly error translations.
"""

import os
import threading
import time
from typing import Optional
import requests
import streamlit as st

from audio_utils import get_wav_duration_seconds

BASE_URL = "https://api.vachana.ai"
_REQUEST_LOCK = threading.Lock()


class GnaniAPIError(Exception):
    """Custom exception containing user-friendly error messages."""
    pass


def get_api_key() -> str:
    """Retrieves GNANI_API_KEY from environment, .env file, or st.secrets safely.

    Never logs, prints, or exposes the key value.
    """
    key = os.getenv("GNANI_API_KEY", "").strip()

    # Fallback to local .env file
    if not key:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GNANI_API_KEY="):
                            key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if key:
                                break
            except Exception:
                pass

    # Fallback to Streamlit secrets (Streamlit Community Cloud)
    if not key:
        try:
            if hasattr(st, "secrets") and "GNANI_API_KEY" in st.secrets:
                key = str(st.secrets["GNANI_API_KEY"]).strip()
        except Exception:
            pass

    return key


def _get_headers() -> dict:
    key = get_api_key()
    if not key:
        raise GnaniAPIError(
            "Gnani API Key is missing. Please set the GNANI_API_KEY environment variable or add it to Streamlit secrets."
        )
    return {"X-API-Key-ID": key}


def _translate_http_error(status_code: int, response_text: str, service_name: str) -> str:
    """Translates raw HTTP errors into clean, informative messages without stack dumps."""
    if status_code in (401, 403):
        return f"{service_name} Authentication Failed: Invalid or expired Gnani API Key. Check GNANI_API_KEY."
    elif status_code == 429:
        return f"{service_name} Rate Limit Exceeded: Only one active request is allowed at a time. Please wait a moment and retry."
    elif status_code == 422:
        return f"{service_name} Input Error (422): The audio or text input format was rejected by the API ({response_text[:120]})."
    elif 500 <= status_code <= 599:
        return f"{service_name} Service Temporarily Unavailable ({status_code}). Please retry in a few seconds."
    return f"{service_name} Request Failed ({status_code}): {response_text[:150]}"


def transcribe(audio_bytes: bytes, language_code: str, file_name: str = "call.wav") -> str:
    """Transcribes audio using Gnani Prisma STT (POST /stt/v3).

    Enforces 60-second limit on WAV inputs.
    """
    if not audio_bytes:
        raise GnaniAPIError("Audio input is empty. Please record or upload a valid audio file.")

    # Pre-check WAV duration limit (60s)
    if file_name.lower().endswith(".wav") or audio_bytes[:4] == b"RIFF":
        dur = get_wav_duration_seconds(audio_bytes)
        if dur is not None and dur > 60.5:
            raise GnaniAPIError(
                f"Audio clip is too long ({dur:.1f}s). Gnani Prisma STT supports audio clips up to 60 seconds."
            )

    headers = _get_headers()
    content_type = "audio/mpeg" if file_name.lower().endswith(".mp3") else "audio/wav"

    with _REQUEST_LOCK:
        # Retry once on 429 rate limit
        for attempt in range(2):
            try:
                response = requests.post(
                    f"{BASE_URL}/stt/v3",
                    headers=headers,
                    files={"audio_file": (file_name, audio_bytes, content_type)},
                    data={"language_code": language_code},
                    timeout=90,
                )
                if response.status_code == 429 and attempt == 0:
                    time.sleep(1.5)
                    continue

                if not response.ok:
                    raise GnaniAPIError(_translate_http_error(response.status_code, response.text, "Prisma STT"))

                data = response.json()
                transcript = data.get("transcript", "")
                if not transcript or not transcript.strip():
                    return ""
                return transcript.strip()

            except requests.Timeout:
                raise GnaniAPIError("Prisma STT timed out. The server took longer than expected to process the audio.")
            except requests.RequestException as e:
                raise GnaniAPIError(f"Network error while connecting to Prisma STT: {e}")

    raise GnaniAPIError("Prisma STT request failed after retry.")


def speak(text: str, voice: str, language: str, sample_rate: int = 24000) -> bytes:
    """Generates speech WAV bytes using Gnani Timbre TTS (POST /api/v1/tts/inference)."""
    if not text or not text.strip():
        raise GnaniAPIError("Cannot synthesize empty text.")

    headers = {**_get_headers(), "Content-Type": "application/json"}
    payload = {
        "text": text.strip(),
        "voice": voice,
        "model": "timbre-v3.0",
        "language": language,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": sample_rate,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav",
        },
    }

    with _REQUEST_LOCK:
        for attempt in range(2):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1/tts/inference",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                if response.status_code == 429 and attempt == 0:
                    time.sleep(1.5)
                    continue

                if not response.ok:
                    raise GnaniAPIError(_translate_http_error(response.status_code, response.text, "Timbre TTS"))

                if not response.content:
                    raise GnaniAPIError("Timbre TTS returned empty audio data.")
                return response.content

            except requests.Timeout:
                raise GnaniAPIError("Timbre TTS timed out. Please retry.")
            except requests.RequestException as e:
                raise GnaniAPIError(f"Network error while connecting to Timbre TTS: {e}")

    raise GnaniAPIError("Timbre TTS request failed after retry.")

