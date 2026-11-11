"""Scam Call Guard - AI-Powered Fraud Defense & Live Call Analysis.

Uses Gnani Prisma (STT) and Gnani Timbre (TTS) with rule-based scoring.
"""

import os
import urllib.parse
import streamlit as st

import audio_utils
import content
import detector
import gnani_client


def play_audio(audio_data: bytes):
    """Plays audio in Streamlit with graceful fallback if autoplay is unsupported."""
    try:
        st.audio(audio_data, format="audio/wav", autoplay=True)
    except TypeError:
        st.audio(audio_data, format="audio/wav")


def render_analysis_results(transcript: str, lang_code: str, lang_name: str, voice_name: str):
    """Renders the immediate visual results: bold banner, transcript, warning audio, tips."""
    if not transcript or not transcript.strip():
        st.warning("⚠️ No audible speech detected in the audio. The transcript is empty.")
        return

    score, reasons, spans, primary = detector.analyze(transcript)

    # 1. Striking Visual Banner (instant impact for demo video)
    if score >= 50:
        css_class = "banner red"
        badge = "🚨 SCAM LIKELY"
    elif score >= 25:
        css_class = "banner amber"
        badge = "⚠️ SUSPICIOUS CALL"
    else:
        css_class = "banner green"
        badge = "✅ LOOKS SAFE"

    st.markdown(
        f'<div class="{css_class}">'
        f'<div class="banner-title">{badge}</div>'
        f'<div class="banner-score">Risk Score: {score}/100</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 2. Transcript Box with trigger phrase highlights
    highlighted_html = detector.highlight(transcript, spans)
    st.markdown(
        f'<div class="call-card">'
        f'<div class="call-card-hdr">📞 Call Audio · Live Transcript (Gnani Prisma)</div>'
        f'<div class="call-card-body">{highlighted_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 3. Localized Scam Tip & Category
    if primary and primary in content.TYPES:
        type_name, tips = content.TYPES[primary]
        st.markdown(
            f'<div class="alert-box">'
            f'<strong>⚠️ Detected Scam Pattern:</strong> {type_name}<br/>'
            f'💡 <em>Advisory Tip:</em> {tips.get(lang_code, tips["en-IN"])}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # 4. Red Flags List
    if reasons:
        st.markdown(f"**Identified Red Flags:** {' · '.join(reasons)}")

    # 5. Timbre TTS Spoken Warning (cached in session_state)
    warning_text = content.WARNINGS[lang_code] if score >= 25 else content.SAFE[lang_code]
    st.write("---")
    st.markdown(f"**🛡️ Voice Security Advisory ({voice_name}):**")

    # Cache key to prevent re-calling Timbre on every rerun
    cache_key = f"tts_{hash((warning_text, voice_name, lang_code))}"
    if cache_key not in st.session_state:
        try:
            with st.spinner("Synthesizing voice alert with Gnani Timbre..."):
                tts_bytes = gnani_client.speak(warning_text, voice_name, lang_code)
                st.session_state[cache_key] = tts_bytes
        except Exception as e:
            st.error(f"TTS Advisory Warning: {e}")
            st.session_state[cache_key] = None

    if st.session_state.get(cache_key):
        play_audio(st.session_state[cache_key])

    st.info(warning_text)

    # 6. Actionable Safeguards: WhatsApp Alert & 1930 Helper
    if score >= 25:
        col_wa, col_cyber = st.columns([1, 1])
        with col_wa:
            if primary and primary in content.TYPES:
                type_name = content.TYPES[primary][0]
                share_template = content.SHARE.get(lang_code, content.SHARE["en-IN"]).format(t=type_name)
                wa_url = "https://wa.me/?text=" + urllib.parse.quote(share_template)
                st.link_button("📲 Share Alert on WhatsApp", wa_url, use_container_width=True)
        with col_cyber:
            st.link_button("🌐 Open Cybercrime Portal (1930)", "https://cybercrime.gov.in", use_container_width=True)

        with st.expander("📝 Copy Official Complaint Summary (for 1930 / cybercrime.gov.in)", expanded=False):
            summary_txt = detector.complaint(transcript, score, primary, reasons, spans, lang_name)
            st.code(summary_txt, language=None)


def main():
    st.set_page_config(
        page_title="Scam Call Guard | Gnani AI",
        page_icon="🛡️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # High-contrast, clean 1080p-optimized styles
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 900px; }
        .banner {
            border-radius: 14px;
            padding: 16px 20px;
            text-align: center;
            color: #ffffff;
            margin: 12px 0 16px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .banner-title { font-size: 1.85rem; font-weight: 800; letter-spacing: 0.5px; }
        .banner-score { font-size: 1.05rem; font-weight: 600; opacity: 0.95; margin-top: 4px; }
        .red { background: linear-gradient(135deg, #b91c1c, #dc2626); box-shadow: 0 0 24px rgba(239, 68, 68, 0.45); }
        .amber { background: linear-gradient(135deg, #b45309, #d97706); }
        .green { background: linear-gradient(135deg, #15803d, #16a34a); }
        
        .call-card {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 12px;
            padding: 14px 18px;
            margin: 10px 0;
            color: #f3f4f6;
        }
        .call-card-hdr { color: #9ca3af; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; }
        .call-card-body { font-size: 1.05rem; line-height: 1.5; }
        .call-card mark {
            background: #ef4444;
            color: #ffffff;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }
        .alert-box {
            background: #1e293b;
            border-left: 5px solid #f59e0b;
            border-radius: 8px;
            padding: 12px 14px;
            margin: 10px 0;
            color: #f1f5f9;
        }
        .sim-badge {
            display: inline-block;
            background: #312e81;
            color: #c7d2fe;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .footer-note {
            text-align: center;
            font-size: 0.82rem;
            color: #9ca3af;
            margin-top: 30px;
            border-top: 1px solid #1f2937;
            padding-top: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🛡️ Scam Call Guard")
    st.caption("AI-Powered Live Fraud Detection & Advisory · Built with Gnani Prisma (STT) & Timbre (TTS)")

    # Architecture Overview Panel
    with st.expander("ℹ️ How it works (Gnani Architecture)", expanded=False):
        st.markdown(
            """
            1. **Audio Input**: Live microphone, recorded audio upload (up to 60s), or generated simulation.
            2. **Gnani Prisma STT (`v3`)**: High-accuracy Indian multilingual speech recognition (Hindi, Marathi, Hinglish, English).
            3. **Heuristic Scam Detector**: Multi-pattern weighted regex analyzing urgency, intimidation, OTP/KYC theft, and authority impersonation.
            4. **Gnani Timbre TTS (`v3.0`)**: Instant local-language voice advisory alert to protect the caller in real time.
            """
        )

    # API Key check with clean guidance
    api_key = gnani_client.get_api_key()
    if not api_key:
        st.error(
            "⚠️ **GNANI_API_KEY Not Configured**\n\n"
            "Please set your environment variable or Streamlit secret:\n"
            "- Local: `set GNANI_API_KEY=your_key` or create a `.env` file.\n"
            "- Streamlit Cloud: add `GNANI_API_KEY = \"your_key\"` to Advanced Settings -> Secrets."
        )
        st.stop()

    # Compact Config Bar (Sensible defaults: Hindi, Shivani voice)
    cfg_col1, cfg_col2 = st.columns([1, 1])
    with cfg_col1:
        lang_name = st.selectbox("Language / बोली", list(content.LANGS.keys()), index=0)
        lang_code = content.LANGS[lang_name]
    with cfg_col2:
        voice_name = st.text_input("Warning Voice (Timbre v3.0)", value="Shivani")

    # Workflow Tabs
    tab_sim, tab_real = st.tabs(["🎭 Scam Call Simulator", "🎙️ Real Audio / Transcript"])
    job_spec = None

    with tab_sim:
        sim_col1, sim_col2 = st.columns([2, 1])
        with sim_col1:
            scripts = content.SCRIPTS.get(lang_code, content.SCRIPTS["hi-IN"])
            script_titles = [s[0] for s in scripts]
            selected_script_title = st.selectbox("Pre-configured Scam Script", script_titles, index=0)
            selected_script = next(s for s in scripts if s[0] == selected_script_title)
        with sim_col2:
            scammer_voice = st.text_input("Scammer Voice (Timbre)", value="Avinash")

        opt_col1, opt_col2 = st.columns([1, 1])
        with opt_col1:
            phone_filter = st.checkbox("📞 Phone line simulation (8 kHz)", value=True)
        with opt_col2:
            noise_level = st.slider("Line Noise Level", 0.0, 1.0, 0.4, 0.1)

        if st.button("▶ Simulate Scam Call", type="primary", use_container_width=True):
            job_spec = ("sim", selected_script, scammer_voice, phone_filter, noise_level)

    with tab_real:
        st.caption("Upload or record actual audio (WAV/MP3 up to 60 seconds), or choose a text sample.")
        mic_audio = st.audio_input("Record Live Audio")
        up_file = st.file_uploader("Upload Audio File (WAV/MP3, max 60s)", type=["wav", "mp3"])

        sample_name = st.selectbox("Or choose a pre-loaded demo sample", list(content.SAMPLES.keys()), index=0)
        manual_text = st.text_area("Or type/paste a transcript manually", value=content.SAMPLES[sample_name], height=80)

        if st.button("🔍 Analyze Call", type="primary", use_container_width=True):
            if mic_audio or up_file or manual_text.strip():
                job_spec = ("real", mic_audio or up_file, manual_text.strip())
            else:
                st.warning("Please provide audio or enter text to analyze.")

    # Execution Handling (Preserve in session_state to prevent re-execution layout flickers)
    if job_spec:
        try:
            if job_spec[0] == "sim":
                _, script_text, tts_lang, scammer_v, phone_flag, noise = (
                    job_spec[1][0],
                    job_spec[1][1],
                    job_spec[1][2],
                    job_spec[2],
                    job_spec[3],
                    job_spec[4],
                )
                with st.spinner("Synthesizing scammer call via Gnani Timbre..."):
                    rate = 8000 if phone_flag else 24000
                    raw_sim_wav = gnani_client.speak(script_text, scammer_v, tts_lang, sample_rate=rate)
                    sim_wav = audio_utils.degrade(raw_sim_wav, noise, target_rate=rate if phone_flag else None)

                st.session_state["sim_audio_cache"] = sim_wav
                st.session_state["sim_noise_val"] = noise

                with st.spinner("Listening & transcribing with Gnani Prisma STT..."):
                    transcript_res = gnani_client.transcribe(sim_wav, lang_code, file_name="simulated_call.wav")
                st.session_state["active_result"] = (transcript_res, lang_code, lang_name, voice_name, "sim")

            elif job_spec[0] == "real":
                audio_obj, manual_str = job_spec[1], job_spec[2]
                st.session_state["sim_audio_cache"] = None

                if manual_str:
                    transcript_res = manual_str
                else:
                    file_bytes = audio_obj.getvalue()
                    fname = getattr(audio_obj, "name", "call.wav")
                    with st.spinner("Transcribing with Gnani Prisma STT..."):
                        transcript_res = gnani_client.transcribe(file_bytes, lang_code, file_name=fname)
                st.session_state["active_result"] = (transcript_res, lang_code, lang_name, voice_name, "real")

        except gnani_client.GnaniAPIError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")

    # Immediately render active results without scrolling
    if "active_result" in st.session_state:
        res_text, res_lang, res_lang_name, res_voice, mode = st.session_state["active_result"]
        if mode == "sim" and st.session_state.get("sim_audio_cache"):
            noise_lbl = f" · Noise: {st.session_state.get('sim_noise_val', 0.4)}"
            st.markdown(f'<div class="sim-badge">🎭 Simulated call generated with Timbre{noise_lbl}</div>', unsafe_allow_html=True)
            play_audio(st.session_state["sim_audio_cache"])

        render_analysis_results(res_text, res_lang, res_lang_name, res_voice)

    # Subtle Mandatory Disclaimer Footer
    st.markdown(
        '<div class="footer-note">'
        'Demo uses simulated calls for educational safety testing. '
        'Report real fraud immediately at national helpline <strong>1930</strong> or '
        '<a href="https://cybercrime.gov.in" target="_blank" style="color:#60a5fa">cybercrime.gov.in</a>.'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
