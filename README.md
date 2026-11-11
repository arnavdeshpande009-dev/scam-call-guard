# 🛡️ Scam Call Guard

> **AI-Powered Fraud Call Defense & Live Advisory**  
> Built for the **Gnani AI "Great Indian AI Internship Challenge"** using **Gnani Prisma (STT)** and **Gnani Timbre (TTS)**.

---

## ⚡ What it Does
Scam Call Guard protects citizens against prevalent Indian telephone fraud (Digital Arrest, Fake Bank KYC, OTP/PIN extortion, Customs Parcel intimidation, and Fake Remote Support).

1. **Input**: Analyzes live recorded speech, uploaded call audio (WAV/MP3), or simulated scam calls.
2. **Speech Recognition**: Powered by **Gnani Prisma STT (`v3`)** for accurate transcription of Indian accents and code-switching (Hindi, Marathi, Hinglish, English).
3. **Detection Engine**: Heuristic weighted pattern matching identifying coercion, urgency, and fraud triggers.
4. **Instant Action & Defense**:
   - **Striking High-Contrast Banner**: Immediate visual alert (`🚨 SCAM LIKELY`, `⚠️ SUSPICIOUS`, `✅ LOOKS SAFE`).
   - **Audio Advisory**: **Gnani Timbre TTS (`v3.0`)** speaks a defense warning in the caller's native language.
   - **WhatsApp Alert**: 1-click button to broadcast a scam alert to family and friends.
   - **1930 Helper**: Auto-generates a ready-to-copy summary for [cybercrime.gov.in](https://cybercrime.gov.in) and National Helpline 1930.

---

## 🏗️ Architecture

```
User Audio / Simulation
         │
         ▼
[ Gnani Prisma STT (v3) ] ──▶ Indian Multilingual Transcript
         │
         ▼
[ Rule-Based Heuristic Detector ]
   ├── Weighted Regex (0-100 Risk Score)
   ├── Scam Classification (Digital Arrest, KYC, OTP, Remote, Parcel, Prize)
   └── Span Highlighter & Complaint Formatter
         │
         ▼
[ Instant Defense & Response UI ]
   ├── Dynamic High-Contrast Status Banner
   ├── Timbre TTS Spoken Warning (Voice: Shivani / Avinash)
   ├── 1-Click WhatsApp Family Alert
   └── 1930 Cybercrime Complaint Helper
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- A valid **Gnani AI API Key** (`X-API-Key-ID`)

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Your API Key
Set your API key via environment variable:
```cmd
set GNANI_API_KEY=your_gnani_api_key_here
```
*(On Linux/macOS: `export GNANI_API_KEY=your_gnani_api_key_here`)*

Alternatively, create a `.env` file based on `.env.example`:
```
GNANI_API_KEY=your_gnani_api_key_here
```

### 4. Run the Application
On Windows, double-click or run:
```cmd
run.bat
```
Or directly with Streamlit:
```bash
streamlit run app.py
```

---

## 🧪 Running Tests
All tests mock external API calls and run completely offline:
```bash
pytest
```

---

## ☁️ Streamlit Community Cloud Deployment
1. Push the repository to GitHub (ensure `.env` and `.streamlit/secrets.toml` remain untracked).
2. Connect your repo in [Streamlit Community Cloud](https://share.streamlit.io).
3. In **App Settings ➔ Secrets**, add:
   ```toml
   GNANI_API_KEY = "your_gnani_api_key_here"
   ```
4. Deploy!

---

## 📹 Demo Video Guide (60 Seconds)
- **First 3 Seconds**: Select **"🎭 Scam Call Simulator"** (default settings: Hindi, Shivani voice, Phone mode, Noise 0.4) and click **"▶ Simulate Scam Call"**.
- The large red **🚨 SCAM LIKELY (Risk Score: 100/100)** banner immediately flashes on screen along with highlighted scam phrases.
- Timbre plays the defensive voice advisory automatically.
- Highlight the **WhatsApp Share** button and **1930 Complaint Helper** expander.

---

## ⚠️ Known Limits & Advisory Note
- **Audio Length**: Prisma STT REST clips support audio up to 60 seconds. WAV files over 60 seconds are caught by a friendly pre-check.
- **Sequential Rate Limits**: Gnani API keys permit one active request at a time. The app uses an internal request lock and 429 auto-retry backoff.
- **Honest Simulation**: Simulated calls are labeled with *"Simulated call generated with Timbre"*.
- *Disclaimer: Demo uses simulated calls for testing and awareness. Report real cyber fraud at 1930 or cybercrime.gov.in.*

