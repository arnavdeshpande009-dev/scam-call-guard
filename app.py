"""Scam Call Guard - AI-Powered Fraud Defense & Live Call Analysis.

Dark Glassmorphic UI optimized for 1920x1080 screen recordings.
Powered by Gnani Prisma (STT) + Timbre (TTS) + Heuristic Scam Scoring.
"""

import html
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


def render_stepper(active_step: int = 0):
    """Renders the 3-step pipeline pill stepper (Prisma STT -> Detector -> Timbre TTS).

    active_step:
        0: idle
        1: Prisma STT active
        2: Detector active
        3: Timbre TTS active / done
    """
    s1_cls = "step-pill step-active" if active_step >= 1 else "step-pill"
    s2_cls = "step-pill step-active" if active_step >= 2 else "step-pill"
    s3_cls = "step-pill step-active" if active_step >= 3 else "step-pill"

    html_code = f"""
    <div class="stepper-wrap">
      <div class="{s1_cls}">
        <span class="step-num">1</span>
        <span>Prisma STT</span>
      </div>
      <div class="step-arrow">→</div>
      <div class="{s2_cls}">
        <span class="step-num">2</span>
        <span>Heuristic Detector</span>
      </div>
      <div class="step-arrow">→</div>
      <div class="{s3_cls}">
        <span class="step-num">3</span>
        <span>Timbre TTS Alert</span>
      </div>
    </div>
    """
    return html_code


def render_analysis_results(transcript: str, lang_code: str, lang_name: str, voice_name: str):
    """Renders dark glassmorphic results immediately visible without scrolling at 1920x1080."""
    if not transcript or not transcript.strip():
        st.warning("⚠️ No audible speech detected in the audio. The transcript is empty.")
        return

    score, reasons, spans, primary = detector.analyze(transcript)

    # 1. Solid High-Impact Banner (red #DC2626 with subtle pulse glow, amber, green)
    if score >= 50:
        banner_cls = "banner-solid banner-red"
        title_text = "🚨 SCAM LIKELY"
        gauge_color = "#EF4444"
    elif score >= 25:
        banner_cls = "banner-solid banner-amber"
        title_text = "⚠️ SUSPICIOUS CALL"
        gauge_color = "#F59E0B"
    else:
        banner_cls = "banner-solid banner-green"
        title_text = "✅ LOOKS SAFE"
        gauge_color = "#10B981"

    st.markdown(
        f"""
        <div class="{banner_cls}">
          <div class="banner-headline">{title_text}</div>
          <div class="banner-sub">Risk Assessment: <strong>{score}/100</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Risk Gauge Bar (0-100)
    st.markdown(
        f"""
        <div class="gauge-container">
          <div class="gauge-header">
            <span>Threat Probability Score</span>
            <span style="color:{gauge_color};font-weight:700;">{score}%</span>
          </div>
          <div class="gauge-track">
            <div class="gauge-fill" style="width:{max(score, 4)}%;background:{gauge_color};"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Phone-call Transcript Card (Avatar, Caller header, Call timer, Highlighted text)
    highlighted_html = detector.highlight(transcript, spans)
    st.markdown(
        f"""
        <div class="glass-card call-card">
          <div class="call-card-top">
            <div class="caller-profile">
              <div class="caller-avatar">👤</div>
              <div>
                <div class="caller-name">Unknown Caller</div>
                <div class="caller-meta">Suspected Fraud Line · 00:24</div>
              </div>
            </div>
            <div class="live-pill">● LIVE TRANSCRIPT</div>
          </div>
          <div class="call-transcript-body">{highlighted_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. Red-Flag Chips (replacing bullet list)
    if reasons:
        chips_html = "".join([f'<span class="flag-chip">⚠️ {html.escape(r)}</span>' for r in reasons])
        st.markdown(
            f"""
            <div class="flags-wrap">
              <span class="flags-label">Detected Flags:</span>
              {chips_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5. Localized Scam-Type Card with Icon & Tip
    if primary and primary in content.TYPES:
        type_name, tips = content.TYPES[primary]
        tip_text = tips.get(lang_code, tips["en-IN"])
        st.markdown(
            f"""
            <div class="glass-card tip-card">
              <div class="tip-title">
                <span class="tip-icon">🛡️</span>
                <span>Identified Modus Operandi: <strong>{html.escape(type_name)}</strong></span>
              </div>
              <div class="tip-body">💡 <em>Advisory Tip:</em> {html.escape(tip_text)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 6. Spoken Voice Warning (Timbre TTS, cached in session_state)
    warning_text = content.WARNINGS[lang_code] if score >= 25 else content.SAFE[lang_code]
    cache_key = f"tts_{hash((warning_text, voice_name, lang_code))}"
    if cache_key not in st.session_state:
        try:
            with st.spinner("Synthesizing voice advisory alert via Gnani Timbre..."):
                tts_bytes = gnani_client.speak(warning_text, voice_name, lang_code)
                st.session_state[cache_key] = tts_bytes
        except Exception as e:
            st.error(f"Voice Advisory Synthesis: {e}")
            st.session_state[cache_key] = None

    if st.session_state.get(cache_key):
        play_audio(st.session_state[cache_key])

    # 7. Action Row: WhatsApp Alert & Cybercrime 1930 Helper
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

        with st.expander("📝 View & Copy Official 1930 Complaint Summary", expanded=False):
            summary_txt = detector.complaint(transcript, score, primary, reasons, spans, lang_name)
            st.code(summary_txt, language=None)


def main():
    st.set_page_config(
        page_title="Scam Call Guard | Gnani AI",
        page_icon="🛡️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # Dark Glassmorphism Custom CSS (Inter + Noto Sans Devanagari)
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

        /* Global Font & Canvas Background */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            color: #F8FAFC;
        }

        /* Hide Streamlit Chrome for clean screen recording */
        #MainMenu, header, footer, [data-testid="stToolbar"], .stDeployButton {
            visibility: hidden !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Canvas Radial Gradient Background */
        .stApp {
            background: #0B1020 radial-gradient(circle at 50% 0%, rgba(124, 58, 237, 0.14) 0%, rgba(6, 182, 212, 0.08) 35%, rgba(11, 16, 32, 0) 70%) !important;
            background-attachment: fixed !important;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 860px !important;
        }

        /* Gradient Brand Header */
        .brand-header {
            text-align: center;
            margin-bottom: 1rem;
        }
        .brand-title {
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #06B6D4 0%, #A855F7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        .brand-sub {
            font-size: 0.95rem;
            color: #CBD5E1;
            font-weight: 500;
            margin-bottom: 0.6rem;
        }
        .brand-badges {
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .lang-badge {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #94A3B8;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 9999px;
            backdrop-filter: blur(8px);
        }

        /* Pipeline Stepper */
        .stepper-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin: 0.75rem 0 1.25rem 0;
        }
        .step-pill {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 9999px;
            padding: 4px 14px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #94A3B8;
            transition: all 0.3s ease;
        }
        .step-active {
            background: rgba(6, 182, 212, 0.14) !important;
            border-color: rgba(6, 182, 212, 0.5) !important;
            color: #22D3EE !important;
            box-shadow: 0 0 16px rgba(6, 182, 212, 0.25);
        }
        .step-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            font-size: 0.7rem;
        }
        .step-active .step-num {
            background: #06B6D4;
            color: #0B1020;
            font-weight: 700;
        }
        .step-arrow {
            color: #475569;
            font-size: 0.85rem;
            font-weight: 700;
        }

        /* Primary Button: Gradient cyan-to-violet */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%) !important;
            border: none !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 1.12rem !important;
            padding: 0.65rem 1.5rem !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35) !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 6px 25px rgba(139, 92, 246, 0.5) !important;
            transform: translateY(-1px) !important;
        }

        /* Dark Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Solid Results Banner (Red #DC2626 with subtle pulsing glow) */
        .banner-solid {
            border-radius: 14px;
            padding: 16px 20px;
            text-align: center;
            color: #FFFFFF;
            margin: 1rem 0 0.8rem 0;
        }
        .banner-red {
            background: #DC2626 !important;
            box-shadow: 0 0 24px rgba(220, 38, 38, 0.55);
            animation: pulse-glow 2.5s infinite ease-in-out;
        }
        .banner-amber {
            background: #D97706 !important;
            box-shadow: 0 0 20px rgba(217, 119, 6, 0.45);
        }
        .banner-green {
            background: #059669 !important;
            box-shadow: 0 0 20px rgba(5, 150, 105, 0.45);
        }
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); }
            50% { box-shadow: 0 0 32px rgba(239, 68, 68, 0.75); }
        }
        .banner-headline {
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: 0.5px;
            line-height: 1.2;
        }
        .banner-sub {
            font-size: 1.02rem;
            font-weight: 500;
            margin-top: 4px;
            opacity: 0.95;
        }

        /* Horizontal Risk Gauge */
        .gauge-container {
            margin: 0.5rem 0 1rem 0;
        }
        .gauge-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            color: #94A3B8;
            margin-bottom: 4px;
        }
        .gauge-track {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            overflow: hidden;
        }
        .gauge-fill {
            height: 100%;
            border-radius: 9999px;
            transition: width 0.6s ease;
        }

        /* Phone Call Transcript Card */
        .call-card {
            padding: 16px 20px;
            margin: 0.85rem 0;
        }
        .call-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 12px;
        }
        .caller-profile {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .caller-avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
        }
        .caller-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #F8FAFC;
        }
        .caller-meta {
            font-size: 0.78rem;
            color: #94A3B8;
        }
        .live-pill {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #F87171;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 9999px;
            letter-spacing: 0.5px;
        }
        .call-transcript-body {
            font-size: 1.05rem;
            line-height: 1.6;
            color: #F1F5F9;
        }
        .call-transcript-body mark {
            background: #DC2626 !important;
            color: #FFFFFF !important;
            padding: 2px 6px;
            border-radius: 5px;
            font-weight: 600;
        }

        /* Red-Flag Chips */
        .flags-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            margin: 0.6rem 0 0.8rem 0;
        }
        .flags-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #94A3B8;
        }
        .flag-chip {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #FCA5A5;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 8px;
        }

        /* Localized Tip Card */
        .tip-card {
            padding: 14px 18px;
            margin: 0.8rem 0;
            border-left: 4px solid #F59E0B;
        }
        .tip-title {
            font-size: 0.95rem;
            color: #F8FAFC;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .tip-body {
            font-size: 0.9rem;
            color: #E2E8F0;
            line-height: 1.5;
        }

        /* Simulation Honest Badge */
        .sim-call-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.35);
            color: #C084FC;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 9999px;
            margin-bottom: 8px;
        }

        /* Subtle Footer */
        .footer-note {
            text-align: center;
            font-size: 0.82rem;
            color: #64748B;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 1. Header Area: Logo, Gradient Title, Subtitle, Language Badges
    st.markdown(
        """
        <div class="brand-header">
          <div class="brand-title">🛡️ Scam Call Guard</div>
          <div class="brand-sub">Powered by Gnani Prisma (STT) + Timbre (TTS)</div>
          <div class="brand-badges">
            <span class="lang-badge">Hindi</span>
            <span class="lang-badge">Marathi</span>
            <span class="lang-badge">Hinglish</span>
            <span class="lang-badge">English</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # API Key check
    api_key = gnani_client.get_api_key()
    if not api_key:
        st.error(
            "⚠️ **GNANI_API_KEY Not Configured**\n\n"
            "Please ensure your key is placed in `.env` (local) or Streamlit Secrets (Cloud)."
        )
        st.stop()

    # 2. Pipeline Stepper Placeholder
    stepper_placeholder = st.empty()
    stepper_placeholder.markdown(render_stepper(active_step=0), unsafe_allow_html=True)

    # 3. Settings & Real Audio Expander (Sensible defaults: Hindi, Shivani voice, noise 0.4, phone on)
    with st.expander("⚙️ Settings & Real Audio (Language, Voices, Noise, Upload)", expanded=False):
        c1, c2 = st.columns([1, 1])
        with c1:
            lang_name = st.selectbox("Call Language", list(content.LANGS.keys()), index=0)
            lang_code = content.LANGS[lang_name]
        with c2:
            voice_name = st.text_input("Warning Voice (Timbre v3.0)", value="Shivani")

        st.markdown("**Simulated Call Customization**")
        scripts = content.SCRIPTS.get(lang_code, content.SCRIPTS["hi-IN"])
        script_titles = [s[0] for s in scripts]
        selected_script_title = st.selectbox("Simulation Script", script_titles, index=0)
        selected_script = next(s for s in scripts if s[0] == selected_script_title)

        scol1, scol2, scol3 = st.columns([1, 1, 1])
        with scol1:
            scammer_voice = st.text_input("Scammer Voice", value="Avinash")
        with scol2:
            phone_filter = st.checkbox("Phone Line Mode (8 kHz)", value=True)
        with scol3:
            noise_level = st.slider("Line Noise", 0.0, 1.0, 0.4, 0.1)

        sim_custom_run = st.button("Simulate with Custom Settings", use_container_width=True)

        st.markdown("---")
        st.markdown("**Real Audio / Manual Transcript**")
        mic_audio = st.audio_input("Record Live Call Audio")
        up_file = st.file_uploader("Upload Audio (WAV/MP3, up to 60s)", type=["wav", "mp3"])
        sample_name = st.selectbox("Demo Samples (No Audio Needed)", list(content.SAMPLES.keys()), index=0)
        manual_text = st.text_area("Or Paste/Type Transcript", value=content.SAMPLES[sample_name], height=70)
        analyze_custom_run = st.button("🔍 Analyze Real Audio / Text", use_container_width=True)

    # 4. One Big Primary Button: "▶ Run demo" (Hindi Digital Arrest, noise 0.4, phone mode on)
    run_demo = st.button("▶ Run demo", type="primary", use_container_width=True)

    # Decide Job Spec
    job_spec = None
    if run_demo:
        # Default 1-click Demo: Hindi Digital Arrest, Avinash, 8 kHz, noise 0.4
        default_script = content.SCRIPTS["hi-IN"][0]  # ("Digital Arrest (CBI / Drugs Parcel)", ...)
        job_spec = ("sim", default_script, "Avinash", True, 0.4, "hi-IN", "Hindi / Hinglish", "Shivani")
    elif sim_custom_run:
        job_spec = ("sim", selected_script, scammer_voice, phone_filter, noise_level, lang_code, lang_name, voice_name)
    elif analyze_custom_run and (mic_audio or up_file or manual_text.strip()):
        job_spec = ("real", mic_audio or up_file, manual_text.strip(), lang_code, lang_name, voice_name)

    # 5. Pipeline Execution with Animated Stepper Progress
    if job_spec:
        try:
            if job_spec[0] == "sim":
                _, script_item, scam_v, phone_f, noise_val, j_lang, j_name, j_voice = job_spec
                _, script_txt, tts_lang = script_item

                # Step 1: Synthesize call & Prisma STT
                stepper_placeholder.markdown(render_stepper(active_step=1), unsafe_allow_html=True)
                with st.spinner("Synthesizing caller speech via Gnani Timbre..."):
                    rate = 8000 if phone_f else 24000
                    raw_wav = gnani_client.speak(script_txt, scam_v, tts_lang, sample_rate=rate)
                    sim_wav = audio_utils.degrade(raw_wav, noise_val, target_rate=rate if phone_f else None)

                st.session_state["sim_audio_cache"] = sim_wav
                st.session_state["sim_noise_val"] = noise_val

                with st.spinner("Prisma STT transcribing call audio..."):
                    transcript_res = gnani_client.transcribe(sim_wav, j_lang, file_name="sim_call.wav")

                # Step 2: Heuristic Detector
                stepper_placeholder.markdown(render_stepper(active_step=2), unsafe_allow_html=True)

                # Step 3: Complete / Timbre Alert Ready
                stepper_placeholder.markdown(render_stepper(active_step=3), unsafe_allow_html=True)
                st.session_state["active_result"] = (transcript_res, j_lang, j_name, j_voice, "sim")

            elif job_spec[0] == "real":
                _, audio_input, manual_str, j_lang, j_name, j_voice = job_spec
                st.session_state["sim_audio_cache"] = None

                stepper_placeholder.markdown(render_stepper(active_step=1), unsafe_allow_html=True)
                if manual_str:
                    transcript_res = manual_str
                else:
                    file_bytes = audio_input.getvalue()
                    fname = getattr(audio_input, "name", "call.wav")
                    with st.spinner("Prisma STT transcribing call audio..."):
                        transcript_res = gnani_client.transcribe(file_bytes, j_lang, file_name=fname)

                stepper_placeholder.markdown(render_stepper(active_step=2), unsafe_allow_html=True)
                stepper_placeholder.markdown(render_stepper(active_step=3), unsafe_allow_html=True)
                st.session_state["active_result"] = (transcript_res, j_lang, j_name, j_voice, "real")

        except gnani_client.GnaniAPIError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")

    # 6. Result Area (Directly below button, visible without scrolling)
    if "active_result" in st.session_state:
        res_text, res_lang, res_lang_name, res_voice, mode = st.session_state["active_result"]
        if mode == "sim" and st.session_state.get("sim_audio_cache"):
            noise_str = f" · Line Noise: {st.session_state.get('sim_noise_val', 0.4)}"
            st.markdown(
                f'<div class="sim-call-badge">🎭 Simulated call generated with Timbre{noise_str}</div>',
                unsafe_allow_html=True,
            )
            play_audio(st.session_state["sim_audio_cache"])

        render_analysis_results(res_text, res_lang, res_lang_name, res_voice)

    # 7. Subtle Footer
    st.markdown(
        """
        <div class="footer-note">
          Demo uses simulated calls. Report real fraud at <strong>1930</strong> / <a href="https://cybercrime.gov.in" target="_blank" style="color:#38BDF8;text-decoration:none;">cybercrime.gov.in</a>.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
