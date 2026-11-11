"""Scam Call Guard v3 - Gnani Prisma (STT) + scam analysis + Gnani Timbre (TTS) warning.
Run: pip install streamlit requests && set GNANI_API_KEY=xxxx && streamlit run app.py
"""
import os
import re
import html
import io
import struct
import wave
import urllib.parse
from datetime import datetime
import numpy as np
import requests
import streamlit as st

API_KEY = os.getenv("GNANI_API_KEY", "")
BASE = "https://api.vachana.ai"
HEADERS = {"X-API-Key-ID": API_KEY}

LANGS = {"Hindi / Hinglish": "hi-IN", "Marathi": "mr-IN", "English (India)": "en-IN"}

# (regex, weight, label, scam type)
RULES = [
    (r"digital arrest|डिजिटल अरेस्ट|डिजिटल अटक", 40, "Digital arrest threat", "arrest"),
    (r"cbi|ed officer|police|crime branch|पुलिस|सीबीआई|सीबीआय|पोलीस", 15, "Impersonating authority", "arrest"),
    (r"otp|ओटीपी|\bpin\b|cvv|पिन", 30, "Asks for OTP/PIN/CVV", "otp"),
    (r"kyc|केवाईसी|केवायसी|account.{0,15}(block|band|बंद)|खात[ाे].{0,10}(बंद|ब्लॉक)", 35, "Fake KYC / account block", "kyc"),
    (r"anydesk|teamviewer|screen share|एनीडेस्क", 30, "Remote-access app request", "remote"),
    (r"arrest|गिरफ्तार|अटक|warrant|वारंट", 20, "Arrest/warrant threat", "arrest"),
    (r"parcel|courier|customs|fedex|पार्सल|कूरियर|कस्टम", 25, "Parcel/customs scam", "parcel"),
    (r"lottery|inam|इनाम|लॉटरी|prize|cashback", 20, "Prize/lottery bait", "prize"),
    (r"transfer|ट्रांसफर|पैसे भेज|पैसे पाठव|upi|यूपीआई|gift card|bitcoin", 20, "Pushes money transfer", "payment"),
    (r"abhi|turant|अभी|तुरंत|लगेच|urgent|immediately|24 hours|किसी को मत बता|kisi ko mat bata|कोणाला सांगू नका", 15, "Urgency / secrecy", None),
]

TYPES = {
    "arrest": ("Digital Arrest / Fake Officer", {
        "hi-IN": "कोई भी सरकारी एजेंसी फोन या वीडियो कॉल पर 'डिजिटल अरेस्ट' नहीं करती। कॉल काटें।",
        "mr-IN": "कोणतीही सरकारी यंत्रणा फोनवर 'डिजिटल अरेस्ट' करत नाही. कॉल कट करा.",
        "en-IN": "No agency arrests anyone over a phone or video call. Hang up."}),
    "kyc": ("Fake KYC / Account Block", {
        "hi-IN": "बैंक कभी फोन पर KYC अपडेट या खाता बंद करने की धमकी नहीं देता। बैंक की ऐप या ब्रांच में जांचें।",
        "mr-IN": "बँक फोनवर KYC किंवा खाते बंद करण्याची धमकी देत नाही. बँकेच्या अॅपमध्ये तपासा.",
        "en-IN": "Banks never threaten to block accounts over a call. Check in your bank's app or branch."}),
    "otp": ("OTP / PIN Fraud", {
        "hi-IN": "OTP, PIN या CVV किसी को न बताएं, बैंक कर्मचारी को भी नहीं।",
        "mr-IN": "OTP, PIN किंवा CVV कोणालाही सांगू नका, बँक कर्मचाऱ्यालाही नाही.",
        "en-IN": "Never share OTP, PIN or CVV with anyone, not even a 'bank employee'."}),
    "remote": ("Remote Access Scam", {
        "hi-IN": "AnyDesk या TeamViewer इंस्टॉल न करें। इससे ठग आपका फोन कंट्रोल कर लेते हैं।",
        "mr-IN": "AnyDesk किंवा TeamViewer इन्स्टॉल करू नका. ठग तुमचा फोन ताब्यात घेतात.",
        "en-IN": "Do not install AnyDesk or TeamViewer. Scammers take over your phone."}),
    "parcel": ("Parcel / Customs Scam", {
        "hi-IN": "अनजान पार्सल या कस्टम फीस के कॉल पर पैसे न भेजें। कूरियर कंपनी से खुद संपर्क करें।",
        "mr-IN": "अनोळखी पार्सल किंवा कस्टम फीसच्या कॉलवर पैसे पाठवू नका.",
        "en-IN": "Do not pay 'customs fees' on a call. Contact the courier company yourself."}),
    "prize": ("Lottery / Prize Scam", {
        "hi-IN": "जो लॉटरी आपने खरीदी नहीं, वो आप जीत नहीं सकते। पहले पैसे मांगे तो ठगी है।",
        "mr-IN": "न घेतलेली लॉटरी तुम्ही जिंकू शकत नाही. आधी पैसे मागितले तर फसवणूक आहे.",
        "en-IN": "You can't win a lottery you never entered. Asking for money first means fraud."}),
    "payment": ("Money Transfer Pressure", {
        "hi-IN": "अनजान कॉलर के कहने पर UPI या ट्रांसफर न करें।",
        "mr-IN": "अनोळखी कॉलरच्या सांगण्यावरून UPI किंवा ट्रान्सफर करू नका.",
        "en-IN": "Never send UPI or transfers because an unknown caller asks."}),
}

WARNINGS = {
    "hi-IN": "सावधान! यह कॉल फ्रॉड हो सकता है। ओटीपी या पिन किसी को न दें, और तुरंत कॉल काट दें। मदद के लिए 1930 पर कॉल करें।",
    "mr-IN": "सावध रहा! हा कॉल फसवणूक असू शकतो. ओटीपी किंवा पिन कोणालाही देऊ नका आणि कॉल कट करा. मदतीसाठी 1930 वर कॉल करा.",
    "en-IN": "Warning! This call may be a scam. Do not share your OTP or PIN, and hang up now. Call 1930 for help.",
}
SAFE = {
    "hi-IN": "इस कॉल में कोई बड़ा खतरा नहीं दिखा, फिर भी ओटीपी किसी को न दें।",
    "mr-IN": "या कॉलमध्ये मोठा धोका दिसला नाही, तरीही ओटीपी कोणालाही देऊ नका.",
    "en-IN": "No major red flags found, but never share your OTP with anyone.",
}
SHARE = {
    "hi-IN": "⚠️ स्कैम अलर्ट: मुझे अभी '{t}' वाला फ्रॉड कॉल आया। ओटीपी/पिन किसी को न बताएं, कॉल काट दें। साइबर हेल्पलाइन: 1930",
    "mr-IN": "⚠️ स्कॅम अलर्ट: मला आत्ताच '{t}' प्रकारचा फसवणूक कॉल आला. OTP/PIN कोणालाही सांगू नका. सायबर हेल्पलाइन: 1930",
    "en-IN": "⚠️ Scam alert: I just got a '{t}' fraud call. Never share OTP/PIN and hang up. Cyber helpline: 1930",
}
SAMPLES = {
    "— pick a demo sample —": "",
    "Hinglish: Digital arrest": "Main CBI officer bol raha hoon, aapka digital arrest ho gaya hai, abhi OTP batao aur kisi ko mat batana.",
    "Hindi: Fake KYC": "आपका खाता बंद होने वाला है, KYC अपडेट करने के लिए तुरंत OTP बताइए।",
    "Marathi: Parcel scam": "तुमच्या नावावर कस्टममध्ये पार्सल अडकले आहे, लगेच UPI ने पैसे पाठवा आणि कोणाला सांगू नका.",
}


def transcribe(audio_bytes: bytes, lang: str) -> str:
    r = requests.post(
        f"{BASE}/stt/v3", headers=HEADERS,
        files={"audio_file": ("call.wav", audio_bytes, "audio/wav")},
        data={"language_code": lang}, timeout=90)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return r.json().get("transcript", "")


def speak(text: str, voice: str, lang: str, rate: int = 24000) -> bytes:
    r = requests.post(
        f"{BASE}/api/v1/tts/inference",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"text": text, "voice": voice, "model": "timbre-v3.0", "language": lang, "speed": 1.0,
              "audio_config": {"sample_rate": rate, "num_channels": 1, "sample_width": 2,
                               "encoding": "linear_pcm", "container": "wav"}},
        timeout=60)
    if not r.ok:
        raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
    return r.content


def analyze(text: str):
    total, reasons, spans, tw = 0, [], [], {}
    for pat, w, label, typ in RULES:
        ms = list(re.finditer(pat, text, re.I))
        if ms:
            total += w
            reasons.append(label)
            spans += [m.span() for m in ms]
            if typ:
                tw[typ] = tw.get(typ, 0) + w
    primary = max(tw, key=tw.get) if tw else None
    return min(100, total), reasons, spans, primary


def highlight(text: str, spans) -> str:
    merged = []
    for a, b in sorted(spans):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(b, merged[-1][1])
        else:
            merged.append([a, b])
    out, pos = "", 0
    for a, b in merged:
        out += html.escape(text[pos:a]) + f"<mark>{html.escape(text[a:b])}</mark>"
        pos = b
    return out + html.escape(text[pos:])



SCRIPTS = {
    "hi-IN": [
        ("Digital arrest (CBI)", "नमस्ते, मैं सीबीआई अधिकारी बोल रहा हूँ। आपके नाम पर एक पार्सल में ड्रग्स मिले हैं और आपका डिजिटल अरेस्ट हो गया है। अभी अपना ओटीपी बताइए और किसी को मत बताइए।", "hi-IN"),
        ("Fake KYC (bank)", "आपका बैंक खाता आज बंद हो जाएगा। केवाईसी अपडेट करने के लिए तुरंत अपना ओटीपी और पिन बताइए।", "hi-IN"),
        ("Hinglish: Digital arrest", "Hello, main CBI officer bol raha hoon. Aapka digital arrest ho gaya hai. Abhi OTP batao aur kisi ko mat batana.", "hi-en"),
    ],
    "mr-IN": [
        ("Parcel / customs", "तुमच्या नावावर कस्टममध्ये पार्सल अडकले आहे. लगेच यूपीआयने पैसे पाठवा आणि कोणाला सांगू नका.", "mr-IN"),
        ("Fake KYC (bank)", "तुमचे बँक खाते आज बंद होणार आहे. केवायसी अपडेट करण्यासाठी लगेच ओटीपी सांगा.", "mr-IN"),
    ],
    "en-IN": [
        ("Digital arrest", "This is a CBI officer. Your digital arrest has been ordered. Share your OTP immediately and do not tell anyone.", "en-IN"),
    ],
}


def degrade(wav_bytes: bytes, noise: float) -> bytes:
    """Rewrite the WAV with a clean header and add hiss + crackle to mimic a bad phone line.
    Parses the header by hand because streamed WAVs can carry invalid length fields."""
    i = wav_bytes.find(b"data")
    if wav_bytes[:4] != b"RIFF" or i < 0:
        return wav_bytes
    ch = struct.unpack("<H", wav_bytes[22:24])[0] or 1
    rate = struct.unpack("<I", wav_bytes[24:28])[0]
    bits = struct.unpack("<H", wav_bytes[34:36])[0]
    if bits != 16:
        return wav_bytes
    pcm = wav_bytes[i + 8:]
    pcm = pcm[: len(pcm) // 2 * 2]
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
    if noise > 0 and len(x):
        rms = float(np.sqrt(np.mean(x ** 2))) + 1e-6
        n = np.random.randn(len(x)).astype(np.float32) * rms * noise
        hits = np.random.rand(len(x)) < 0.0005 * noise
        n[hits] += rms * 3 * np.random.randn(int(hits.sum()))
        x = x + n
    y = np.clip(x, -32768, 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as o:
        o.setnchannels(ch)
        o.setsampwidth(2)
        o.setframerate(rate)
        o.writeframes(y.tobytes())
    return buf.getvalue()


def complaint(text, s, primary, reasons, spans, lang_name):
    phrases = sorted({text[a:b].strip().lower() for a, b in spans})
    kind = TYPES[primary][0] if primary else "Suspicious call"
    return (
        "SCAM CALL COMPLAINT SUMMARY\n"
        f"Date/time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
        f"Scam type: {kind}\n"
        f"Risk score: {s}/100\n"
        f"Call language: {lang_name}\n"
        f"Red flags: {', '.join(reasons) or 'none'}\n"
        f"Key phrases heard: {', '.join(phrases) or 'none'}\n"
        f"Transcript: {text}\n\n"
        "Report at: https://cybercrime.gov.in  |  Helpline: 1930\n"
        "Caller number: (add the number that called you)"
    )


def play(audio: bytes):
    try:
        st.audio(audio, format="audio/wav", autoplay=True)
    except TypeError:
        st.audio(audio, format="audio/wav")


def render_result(text, lang, lang_name, voice):
    s, reasons, spans, primary = analyze(text)
    cls, label = ("red", "🚨 SCAM LIKELY") if s >= 50 else ("amber", "⚠️ SUSPICIOUS") if s >= 25 else ("green", "✅ LOOKS SAFE")
    st.markdown(f'<div class="banner {cls}">{label}<div style="font-size:1rem;font-weight:500">Risk score {s}/100</div></div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="call"><div class="hd">📞 Incoming call · live transcript (Gnani Prisma)</div>{highlight(text, spans) or "(empty)"}</div>',
                unsafe_allow_html=True)
    if primary:
        name, tips = TYPES[primary]
        st.subheader(f"Scam type: {name}")
        st.markdown(f'<div class="tip">💡 {tips[lang]}</div>', unsafe_allow_html=True)
    if reasons:
        st.write("**Red flags:** " + " · ".join(reasons))
    msg = WARNINGS[lang] if s >= 25 else SAFE[lang]
    try:
        play(speak(msg, voice, lang))
    except Exception as e:
        st.warning(f"TTS failed: {e}")
    st.info(msg)
    if s >= 25:
        if primary:
            share = SHARE[lang].format(t=TYPES[primary][0])
            st.link_button("📲 Share alert with family on WhatsApp", "https://wa.me/?text=" + urllib.parse.quote(share))
        st.subheader("📝 Complaint helper")
        st.caption("Copy this and report at cybercrime.gov.in or call 1930.")
        st.code(complaint(text, s, primary, reasons, spans, lang_name), language=None)
        st.link_button("Open cybercrime.gov.in", "https://cybercrime.gov.in")


st.set_page_config(page_title="Scam Call Guard", page_icon="🛡️")
st.markdown("""
<style>
.call{background:#111827;border:1px solid #1f2937;border-radius:18px;padding:18px 20px;margin:10px 0;color:#e5e7eb}
.call .hd{color:#9ca3af;font-size:.85rem;margin-bottom:8px}
.call mark{background:#dc2626;color:#fff;padding:1px 5px;border-radius:5px}
.banner{border-radius:16px;padding:22px;text-align:center;font-size:2rem;font-weight:800;color:#fff;margin:12px 0}
.red{background:#b91c1c;box-shadow:0 0 28px #ef4444aa}.amber{background:#b45309}.green{background:#15803d}
.tip{background:#1f2937;border-left:5px solid #f59e0b;border-radius:10px;padding:12px 16px;color:#f3f4f6}
</style>""", unsafe_allow_html=True)
st.title("🛡️ Scam Call Guard")
st.caption("Powered by Gnani Prisma (STT) + Timbre (TTS) · #GnaniAI #GreatIndianAIInternshipChallenge")

if not API_KEY:
    st.error("Set GNANI_API_KEY environment variable first.")
    st.stop()

c1, c2 = st.columns(2)
lang_name = c1.selectbox("Call language", list(LANGS))
lang = LANGS[lang_name]
voice = c2.text_input("Warning voice (Timbre v3.0)", "Shivani")

job = None
tab_sim, tab_real = st.tabs(["🎭 Scam call simulator", "🎙️ Real audio / text"])

with tab_sim:
    st.caption("Timbre plays the scammer, Prisma listens, the detector reacts. No recording needed.")
    scripts = SCRIPTS[lang]
    pick = st.selectbox("Scam script", [t for t, _, _ in scripts])
    scammer = st.text_input("Scammer voice", "Avinash")
    phone = st.checkbox("📞 Phone-line quality (8 kHz)", value=True)
    noise = st.slider("Background noise", 0.0, 1.5, 0.4, 0.1)
    if st.button("▶ Simulate scam call", type="primary"):
        job = ("sim", next(s for s in scripts if s[0] == pick))

with tab_real:
    mic = st.audio_input("Record the call audio")
    up = st.file_uploader("...or upload a call recording (WAV/MP3, up to 60s)", type=["wav", "mp3"])
    sample = st.selectbox("Demo samples (no audio needed)", list(SAMPLES))
    manual = st.text_area("Or paste a transcript", value=SAMPLES[sample])
    if st.button("Analyze call") and ((mic or up) or manual):
        job = ("real", (mic or up, manual))

if job:
    try:
        if job[0] == "sim":
            _, text_in, tts_lang = job[1]
            with st.spinner("Placing the scam call..."):
                wav = speak(text_in, scammer, tts_lang, 8000 if phone else 24000)
                wav = degrade(wav, noise)
            st.caption("🔊 Simulated scam call (generated with Timbre)" + (f", noise {noise}" if noise else ""))
            play(wav)
            with st.spinner("Listening..."):
                text = transcribe(wav, lang)
        else:
            audio, manual_text = job[1]
            with st.spinner("Listening..."):
                text = manual_text or transcribe(audio.getvalue(), lang)
    except Exception as e:
        st.error(f"Failed: {e}")
        st.stop()
    render_result(text, lang, lang_name, voice)