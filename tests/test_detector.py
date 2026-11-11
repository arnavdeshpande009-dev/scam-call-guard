"""Tests for detector rules, scoring, scam classification, highlighting, and complaint formatting."""

import pytest
import detector
import content


# Test at least 3 scripts per language (Hindi, Marathi, Hinglish/English)
SCRIPTS_TO_TEST = [
    # Hindi
    ("hi_arrest", "नमस्ते मैं सीबीआई क्राइम ब्रांच से बोल रहा हूँ आपका डिजिटल अरेस्ट हो चुका है अभी ओटीपी बताइए और किसी को मत बताइए।", "arrest", 50),
    ("hi_kyc", "आपका बैंक खाता तुरंत बंद हो जाएगा, केवाईसी अपडेट करने के लिए तुरंत ओटीपी और पिन बताइए।", "kyc", 50),
    ("hi_lottery", "आपने 25 लाख की लॉटरी जीती है, तुरंत खाते में पैसे ट्रांसफर करें और किसी को मत बताइए।", "prize", 35),
    # Marathi
    ("mr_customs", "तुमच्या नावावर कस्टममध्ये पार्सल अडकले आहे. अटक टाळण्यासाठी लगेच यूपीआयने पैसे पाठवा आणि कोणाला सांगू नका.", "parcel", 40),
    ("mr_kyc", "तुमचे बँक खाते आज बंद होणार आहे, केवायसी अपडेट करण्यासाठी लगेच ओटीपी आणि पिन सांगा.", "kyc", 50),
    ("mr_remote", "बँकेतून बोलत आहे, तुमच्या मोबाईलमध्ये लगेच एनीडेस्क किंवा स्क्रीन शेअर ॲप चालू करा.", "remote", 30),
    # Hinglish & English
    ("hinglish_arrest", "Hello, main CBI officer bol raha hoon. Aapka digital arrest ho gaya hai. Abhi OTP batao aur kisi ko mat batana.", "arrest", 50),
    ("en_arrest", "This is Crime Branch police. A warrant is issued and your digital arrest is confirmed. Share OTP immediately.", "arrest", 50),
    ("en_remote", "Your computer has a virus. Please install AnyDesk screen share immediately so we can fix it.", "remote", 45),
    # Benign / Safe
    ("benign_hi", "नमस्ते भाई, कल शाम को चाय पीने चलेंगे। समय पर आ जाना।", None, 0),
]


@pytest.mark.parametrize("name, text, expected_type, min_score", SCRIPTS_TO_TEST)
def test_detector_scoring_and_classification(name, text, expected_type, min_score):
    score, reasons, spans, primary = detector.analyze(text)
    assert score >= min_score, f"Script {name} scored {score}, expected at least {min_score}"
    if expected_type:
        assert primary == expected_type, f"Script {name} classified as {primary}, expected {expected_type}"
        assert len(reasons) > 0
        assert len(spans) > 0
    else:
        assert primary is None
        assert score == 0


def test_highlight_merging():
    """Verify that overlapping and adjacent spans are merged properly without nested <mark> tags."""
    text = "CBI officer arrest warrant"
    # Overlapping spans: "CBI officer" (0, 11) and "officer arrest" (4, 18)
    spans = [(0, 11), (4, 18)]
    rendered = detector.highlight(text, spans)
    assert "<mark>CBI officer arrest</mark> warrant" == rendered
    assert rendered.count("<mark>") == 1
    assert rendered.count("</mark>") == 1


def test_highlight_html_escaping():
    """Ensure raw HTML chars in text are safely escaped."""
    text = "Check <script>alert(1)</script> CBI officer"
    spans = [(32, 43)]
    rendered = detector.highlight(text, spans)
    assert "&lt;script&gt;" in rendered
    assert "<mark>CBI officer</mark>" in rendered


def test_complaint_helper_format():
    """Verify complaint helper text structure and essential reporting fields."""
    text = "Main CBI officer bol raha hoon, digital arrest hai, OTP do."
    score, reasons, spans, primary = detector.analyze(text)
    summary = detector.complaint(text, score, primary, reasons, spans, "Hindi / Hinglish")

    assert "SCAM CALL COMPLAINT SUMMARY" in summary
    assert "Digital Arrest" in summary
    assert f"Risk Score: {score}/100" in summary
    assert "https://cybercrime.gov.in" in summary
    assert "1930" in summary
    assert "Main CBI officer bol raha hoon" in summary
