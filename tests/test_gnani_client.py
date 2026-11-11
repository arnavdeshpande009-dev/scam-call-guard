"""Tests for Gnani API client with mocked network calls and error conditions."""

from unittest.mock import MagicMock, patch
import requests
import pytest

import gnani_client
from gnani_client import GnaniAPIError
from tests.test_audio_utils import create_dummy_wav


def test_missing_api_key(monkeypatch):
    monkeypatch.setenv("GNANI_API_KEY", "")
    with patch("streamlit.secrets", {}), patch("os.path.exists", return_value=False):
        with pytest.raises(GnaniAPIError) as exc:
            gnani_client.transcribe(b"dummy", "hi-IN")
        assert "Gnani API Key is missing" in str(exc.value)


@patch("gnani_client.get_api_key", return_value="dummy_key_12345")
@patch("requests.post")
def test_transcribe_success(mock_post, mock_key):
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"transcript": "Main CBI se bol raha hoon"}
    mock_post.return_value = mock_resp

    wav = create_dummy_wav(duration_sec=2.0)
    res = gnani_client.transcribe(wav, "hi-IN")

    assert res == "Main CBI se bol raha hoon"
    assert mock_post.call_count == 1
    # Verify auth header is present
    headers = mock_post.call_args[1]["headers"]
    assert headers["X-API-Key-ID"] == "dummy_key_12345"


@patch("gnani_client.get_api_key", return_value="dummy_key_12345")
@patch("requests.post")
def test_transcribe_clip_over_60s_rejected(mock_post, mock_key):
    """Enforce pre-check on WAV clips longer than 60s."""
    long_wav = create_dummy_wav(duration_sec=65.0)
    with pytest.raises(GnaniAPIError) as exc:
        gnani_client.transcribe(long_wav, "hi-IN", "long.wav")
    assert "too long" in str(exc.value)
    # Ensure network request was never sent
    assert mock_post.call_count == 0


@patch("gnani_client.get_api_key", return_value="dummy_key_12345")
@patch("requests.post")
def test_rate_limit_429_retry_success(mock_post, mock_key):
    """Should retry once on 429 and succeed if 2nd attempt succeeds."""
    resp_429 = MagicMock()
    resp_429.ok = False
    resp_429.status_code = 429

    resp_200 = MagicMock()
    resp_200.ok = True
    resp_200.status_code = 200
    resp_200.content = b"RIFF....WAVBYTES"

    mock_post.side_effect = [resp_429, resp_200]

    audio = gnani_client.speak("सावधान", "Shivani", "hi-IN")
    assert audio == b"RIFF....WAVBYTES"
    assert mock_post.call_count == 2


@patch("gnani_client.get_api_key", return_value="dummy_key_12345")
@patch("requests.post")
def test_auth_failure_401(mock_post, mock_key):
    resp_401 = MagicMock()
    resp_401.ok = False
    resp_401.status_code = 401
    resp_401.text = "Unauthorized key"
    mock_post.return_value = resp_401

    with pytest.raises(GnaniAPIError) as exc:
        gnani_client.speak("Test", "Shivani", "en-IN")
    assert "Authentication Failed" in str(exc.value)


@patch("gnani_client.get_api_key", return_value="dummy_key_12345")
@patch("requests.post")
def test_input_error_422(mock_post, mock_key):
    resp_422 = MagicMock()
    resp_422.ok = False
    resp_422.status_code = 422
    resp_422.text = "Unprocessable entity"
    mock_post.return_value = resp_422

    with pytest.raises(GnaniAPIError) as exc:
        gnani_client.transcribe(create_dummy_wav(1.0), "hi-IN")
    assert "Input Error (422)" in str(exc.value)


@patch("gnani_client.get_api_key", return_value="dummy_key_12345")
@patch("requests.post")
def test_timeout_handled_gracefully(mock_post, mock_key):
    mock_post.side_effect = requests.Timeout("Connection timed out")
    with pytest.raises(GnaniAPIError) as exc:
        gnani_client.speak("Alert", "Shivani", "en-IN")
    assert "timed out" in str(exc.value)

