# 🛡️ Scam Call Guard

**Catch Indian phone scams in Hindi, Marathi, Hinglish and English, then warn the listener out loud.**

Built for the **Gnani AI "Great Indian AI Internship Challenge"** with **Gnani Prisma** (speech-to-text) and **Gnani Timbre** (text-to-speech).

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-26%20passing-brightgreen)](#-testing)
[![Gnani](https://img.shields.io/badge/Powered%20by-Gnani%20AI-6C47FF)](https://gnani.ai)

**🔗 Live demo:** `ADD_YOUR_STREAMLIT_LINK_HERE`  
**🎥 Demo video:** `ADD_YOUR_LINKEDIN_OR_X_POST_LINK_HERE`

> `#GnaniAI` `#GreatIndianAIInternshipChallenge`

<!-- Add a screenshot or GIF here: ![Scam Call Guard demo](docs/demo.gif) -->

---

## 📌 The Problem

"Digital arrest", fake KYC, OTP theft and customs-parcel threats reach Indians every day, usually in regional languages and over poor phone lines. Victims are pressured into acting before they can think. Most existing tools are English-first and do not handle code-mixed speech or noisy telephone audio.

## 💡 The Solution

Scam Call Guard listens to a call recording (or a simulated call), transcribes it with **Gnani Prisma**, scores it against known scam patterns, and immediately:

- shows a clear **SCAM LIKELY / SUSPICIOUS / LOOKS SAFE** verdict,
- highlights the exact manipulative phrases,
- names the scam type and explains it in plain language,
- **speaks a warning** in the caller's language using **Gnani Timbre**,
- lets the user alert family on WhatsApp and prepare a complaint for **1930 / cybercrime.gov.in**.

---

## ✨ Features

| Area | What it does |
|---|---|
| **Multilingual STT** | Gnani Prisma transcribes Hindi / Hinglish, Marathi and English (India) from microphone recordings or uploaded WAV/MP3 files (up to 60 seconds). |
| **Scam detection** | Weighted rule engine (0–100 risk score) with patterns in Devanagari and romanized Hinglish. Fully explainable, no black box. |
| **Scam classification** | Digital Arrest / Fake Officer, Fake KYC, OTP/PIN fraud, Remote Access, Parcel/Customs, Lottery/Prize, Money Transfer pressure. |
| **Phrase highlighting** | Trigger phrases are marked in red inside a phone-call style transcript. |
| **Spoken warning** | Gnani Timbre voices a localized advisory, autoplayed in the browser. |
| **Safety tips** | Plain-language guidance per scam type in Hindi, Marathi and English. |
| **Scam call simulator** | Timbre plays the scammer, Prisma transcribes, the detector reacts, all in one screen with no recordings needed. |
| **Phone-line mode** | 8 kHz telephone-quality audio plus an adjustable hiss/crackle noise slider to test robustness. |
| **WhatsApp alert** | One tap opens WhatsApp with a ready family alert in the selected language. |
| **Complaint helper** | Copy-ready summary (time, scam type, score, key phrases, transcript) for 1930 and cybercrime.gov.in. |
| **Modern UI** | Dark glassmorphism interface with a solid, high-contrast alert banner, designed for screen recording. |

### Award categories this project targets
Regional languages · Hinglish / code-mixed voice · Noisy telephonic audio · Real-world impact · Best solo/duo project · Best 60-second demo

---

## 🏗️ Architecture

```
 Call audio (mic / upload / simulated by Timbre)
                    │
                    ▼
        ┌────────────────────────┐
        │  Gnani Prisma STT (v3) │  →  Multilingual transcript
        └────────────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │  Rule-based detector   │  →  Risk score, scam type,
        │  (detector.py)         │     highlighted spans
        └────────────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │  Response UI (Streamlit)│
        │  • Verdict banner      │
        │  • Timbre TTS warning  │
        │  • WhatsApp alert      │
        │  • 1930 complaint text │
        └────────────────────────┘
```

### Project structure

```
├── app.py              # Streamlit UI
├── gnani_client.py     # Prisma STT + Timbre TTS client (retries, error mapping)
├── detector.py         # Scoring, classification, highlighting, complaint text
├── audio_utils.py      # WAV parsing, duration check, 8 kHz + noise simulation
├── content.py          # Languages, scripts, tips, warnings, share text
├── tests/              # Offline pytest suite (network fully mocked)
├── requirements.txt    # Pinned dependencies
├── .env.example        # API key template
└── run.bat             # One-click Windows launcher
```

### Why rule-based detection?
Scam scripts follow strong, repeated patterns (authority impersonation, urgency, secrecy, requests for OTP/PIN or money). A weighted rule engine is fast, works offline after transcription, and every verdict can be explained by pointing at the exact words that triggered it, which matters when the output tells someone to hang up.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or newer
- A Gnani API key from [app.gnani.ai](https://app.gnani.ai) (sent as the `X-API-Key-ID` header)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/scam-call-guard.git
cd scam-call-guard
pip install -r requirements.txt
```

### Configure your key

Copy `.env.example` to `.env` and add your key:

```
GNANI_API_KEY=your_gnani_api_key_here
```

Or set it as an environment variable:

```cmd
:: Windows (cmd)
set GNANI_API_KEY=your_gnani_api_key_here
```
```bash
# macOS / Linux
export GNANI_API_KEY=your_gnani_api_key_here
```

> 🔐 **Never commit your key.** `.env` is git-ignored. If a key is ever exposed, delete it in the Gnani dashboard and create a new one.

### Run

```bash
python -m streamlit run app.py
```

On Windows you can also double-click `run.bat`. The app opens at `http://localhost:8501`.

---

## 🎬 Quick Demo

1. Open the app and click **▶ Run demo** (Hindi, phone-line mode on, noise 0.4).
2. Timbre plays a simulated scam call; Prisma transcribes it.
3. The red **SCAM LIKELY** banner appears with highlighted phrases, the scam type and a tip.
4. The Timbre voice warning plays automatically.
5. Open **Settings** to try Marathi or Hinglish, raise the noise, or analyze your own recording.
6. Use the WhatsApp button and the complaint helper.

---

## 🧪 Testing

All 26 tests run offline with network calls mocked:

```bash
pytest
```

They cover detector scoring and classification across languages, span highlighting, WAV parsing and degradation (including streamed WAV headers with invalid length fields), duration limits, and API error handling (401, 422, 429 retry, timeouts).

---

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (confirm `.env` is not tracked).
2. Create an app at [share.streamlit.io](https://share.streamlit.io) pointing to `app.py`.
3. Under **Advanced settings → Secrets**, add:
   ```toml
   GNANI_API_KEY = "your_gnani_api_key_here"
   ```
4. Deploy.

Note: a public deployment spends the credits tied to your key. Share the link thoughtfully.

---

## 🔒 Privacy & Responsible Use

- Audio and text are sent to Gnani's APIs for transcription and speech synthesis. Review Gnani's terms before using real recordings.
- The app keeps results in the Streamlit session only and does not include a database.
- The demo call is **simulated with Timbre** and is labeled as such in the UI.
- This tool analyzes **recorded or simulated** calls. It does not intercept live phone calls.
- It is an awareness and assistance tool, not a guarantee. If you suspect fraud, **hang up and report it at 1930 or [cybercrime.gov.in](https://cybercrime.gov.in)**.

---

## ⚠️ Known Limitations

- Prisma REST requests accept clips up to **60 seconds**; longer WAV files are rejected with a clear message.
- Gnani keys allow **one active request at a time**; the app serializes calls and retries once on rate limits.
- Rule-based detection can miss novel scripts and may flag legitimate calls that use similar words. Accuracy also depends on transcript quality, especially at high noise levels.
- Marathi and other regional rules are a starting set and benefit from real-world samples.

---

## 🗺️ Roadmap

- Live streaming transcription with Prisma's realtime API so the alert fires mid-call
- Evon-powered explanations and a learned scam classifier alongside the rules
- Warning in a trusted family member's voice using voice cloning
- More Indian languages supported by Gnani
- Mobile-friendly app and a "forward this recording" flow

---

## 🙏 Acknowledgements

- [Gnani AI](https://gnani.ai) for the Prisma and Timbre models and the Great Indian AI Internship Challenge
- [Streamlit](https://streamlit.io) for the app framework

## 👤 Author

**Arnav Deshpande**  
B.Tech CSE, Dnyaan Prasad Global University, Pune 
