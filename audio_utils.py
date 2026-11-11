"""Audio utilities for WAV inspection, streaming header resilience, and phone-line degradation."""

import io
import struct
import wave
from typing import Optional
import numpy as np


def get_wav_duration_seconds(audio_bytes: bytes) -> Optional[float]:
    """Calculates the duration in seconds of a WAV byte stream by parsing headers manually.

    Handles streamed or non-standard headers where chunk lengths might be missing or 0xFFFFFFFF.
    Returns None if the audio is not a recognizable WAV format or cannot be parsed.
    """
    if len(audio_bytes) < 44 or audio_bytes[:4] != b"RIFF" or audio_bytes[8:12] != b"WAVE":
        return None

    try:
        # Find 'fmt ' chunk
        fmt_idx = audio_bytes.find(b"fmt ")
        if fmt_idx >= 0 and len(audio_bytes) >= fmt_idx + 24:
            # fmt chunk layout:
            # +0: 'fmt ' (4 bytes)
            # +4: fmt chunk size (4 bytes)
            # +8: audio_format (2 bytes, 1 = PCM)
            # +10: num_channels (2 bytes)
            # +12: sample_rate (4 bytes)
            # +16: byte_rate (4 bytes)
            # +20: block_align (2 bytes)
            # +22: bits_per_sample (2 bytes)
            channels = int(struct.unpack("<H", audio_bytes[fmt_idx + 10 : fmt_idx + 12])[0])
            sample_rate = int(struct.unpack("<I", audio_bytes[fmt_idx + 12 : fmt_idx + 16])[0])
            bits_per_sample = int(struct.unpack("<H", audio_bytes[fmt_idx + 22 : fmt_idx + 24])[0])

            # Find 'data' chunk
            data_idx = audio_bytes.find(b"data")
            if data_idx >= 0:
                pcm_bytes_len = len(audio_bytes) - (data_idx + 8)
                bytes_per_sample = bits_per_sample // 8
                bytes_per_second = sample_rate * channels * bytes_per_sample

                if bytes_per_second > 0 and pcm_bytes_len > 0:
                    return float(pcm_bytes_len) / float(bytes_per_second)
    except Exception:
        pass

    # Fallback to wave reader
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate > 0:
                return float(frames) / float(rate)
    except Exception:
        return None

    return None


def degrade(wav_bytes: bytes, noise: float, target_rate: Optional[int] = None) -> bytes:
    """Rewrites the WAV with a clean standard 16-bit PCM header and applies phone-line noise/crackle.

    Resilient to streamed WAV chunks and invalid length fields by hand-locating the 'data' chunk.
    If the file is not 16-bit PCM or not a valid RIFF WAV, returns original bytes safely.
    """
    if len(wav_bytes) < 44 or wav_bytes[:4] != b"RIFF":
        return wav_bytes

    data_idx = wav_bytes.find(b"data")
    if data_idx < 0:
        return wav_bytes

    fmt_idx = wav_bytes.find(b"fmt ")
    if fmt_idx >= 0 and len(wav_bytes) >= fmt_idx + 24:
        channels = int(struct.unpack("<H", wav_bytes[fmt_idx + 10 : fmt_idx + 12])[0]) or 1
        rate = int(struct.unpack("<I", wav_bytes[fmt_idx + 12 : fmt_idx + 16])[0])
        bits = int(struct.unpack("<H", wav_bytes[fmt_idx + 22 : fmt_idx + 24])[0])
    else:
        channels = int(struct.unpack("<H", wav_bytes[22:24])[0]) or 1
        rate = int(struct.unpack("<I", wav_bytes[24:28])[0])
        bits = int(struct.unpack("<H", wav_bytes[34:36])[0])

    # Only process 16-bit PCM audio
    if bits != 16 or rate == 0:
        return wav_bytes

    pcm = wav_bytes[data_idx + 8 :]
    # Align to 16-bit (2 bytes per sample)
    pcm = pcm[: len(pcm) // 2 * 2]
    if not pcm:
        return wav_bytes

    try:
        samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
        if noise > 0 and len(samples) > 0:
            rms = float(np.sqrt(np.mean(samples**2))) + 1e-6
            hiss = np.random.randn(len(samples)).astype(np.float32) * rms * noise
            # Occasional line crackle / drops
            hits = np.random.rand(len(samples)) < (0.0005 * noise)
            hiss[hits] += rms * 3 * np.random.randn(int(hits.sum()))
            samples = samples + hiss

        processed = np.clip(samples, -32768, 32767).astype(np.int16)

        out_rate = int(target_rate) if target_rate else int(rate)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(int(channels))
            wf.setsampwidth(2)
            wf.setframerate(out_rate)
            wf.writeframes(processed.tobytes())
        return buf.getvalue()
    except Exception:
        return wav_bytes
