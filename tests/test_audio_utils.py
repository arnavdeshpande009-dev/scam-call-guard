"""Tests for audio utilities: WAV header parsing, streamed headers, and degradation."""

import io
import wave
import numpy as np
import pytest
import audio_utils


def create_dummy_wav(channels: int = 1, rate: int = 8000, duration_sec: float = 1.0, bits: int = 16) -> bytes:
    """Helper to generate a valid PCM WAV in memory with strict integer parameters."""
    buf = io.BytesIO()
    int_channels = int(channels)
    int_rate = int(rate)
    num_samples = int(int_rate * duration_sec)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    # 440 Hz sine tone
    samples = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)

    with wave.open(buf, "wb") as wf:
        wf.setnchannels(int_channels)
        wf.setsampwidth(int(bits // 8))
        wf.setframerate(int_rate)
        wf.writeframes(samples.tobytes())
    return buf.getvalue()


def test_wav_duration_valid():
    wav_bytes = create_dummy_wav(duration_sec=2.5, rate=16000)
    dur = audio_utils.get_wav_duration_seconds(wav_bytes)
    assert dur is not None
    assert pytest.approx(dur, rel=0.05) == 2.5


def test_wav_duration_streamed_invalid_length_field():
    """Streamed WAV files often have chunk length or RIFF size set to 0 or 0xFFFFFFFF."""
    wav_bytes = bytearray(create_dummy_wav(duration_sec=3.0, rate=8000))
    # Corrupt the RIFF file size field at offset 4..8
    wav_bytes[4:8] = b"\xff\xff\xff\xff"
    # Corrupt data chunk size field
    data_idx = wav_bytes.find(b"data")
    if data_idx >= 0:
        wav_bytes[data_idx + 4 : data_idx + 8] = b"\x00\x00\x00\x00"

    dur = audio_utils.get_wav_duration_seconds(bytes(wav_bytes))
    assert dur is not None
    assert pytest.approx(dur, rel=0.05) == 3.0


def test_wav_duration_non_wav():
    """Non-WAV files (e.g. MP3 or arbitrary bytes) should return None safely."""
    dummy_mp3 = b"\xff\xfb\x90\x64" + b"\x00" * 500
    assert audio_utils.get_wav_duration_seconds(dummy_mp3) is None
    assert audio_utils.get_wav_duration_seconds(b"") is None


def test_audio_degrade_phone_simulation():
    """Verify degrade adds noise and preserves/rewrites clean playable WAV."""
    orig_wav = create_dummy_wav(duration_sec=1.0, rate=8000)
    degraded = audio_utils.degrade(orig_wav, noise=0.4, target_rate=8000)

    assert len(degraded) > 44
    assert degraded[:4] == b"RIFF"

    # Verify output is readable by standard wave module
    with wave.open(io.BytesIO(degraded), "rb") as wf:
        assert wf.getframerate() == 8000
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getnframes() > 0


def test_audio_degrade_streamed_header():
    """Verify degrade works on streamed WAV with corrupted size fields."""
    wav_bytes = bytearray(create_dummy_wav(duration_sec=1.5, rate=8000))
    wav_bytes[4:8] = b"\xff\xff\xff\xff"  # Corrupt size
    degraded = audio_utils.degrade(bytes(wav_bytes), noise=0.2)

    with wave.open(io.BytesIO(degraded), "rb") as wf:
        frames = wf.getnframes()
        assert frames > 0
        rate = wf.getframerate()
        assert pytest.approx(frames / rate, rel=0.1) == 1.5


def test_audio_degrade_non_16bit():
    """Should safely return original bytes without error if not 16-bit PCM."""
    wav_8bit = create_dummy_wav(duration_sec=0.5, bits=8)
    res = audio_utils.degrade(wav_8bit, noise=0.5)
    # Must return without crashing
    assert res == wav_8bit
