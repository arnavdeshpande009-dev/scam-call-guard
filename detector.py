"""Rule-based scam detection, scoring, classification, and report generation."""

import re
import html
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from content import RULES, TYPES


def analyze(text: str) -> Tuple[int, List[str], List[Tuple[int, int]], Optional[str]]:
    """Analyzes text against regex rules.

    Returns:
        score: Integer risk score bounded between 0 and 100.
        reasons: List of human-readable red flag labels.
        spans: List of (start_idx, end_idx) character spans for detected phrases.
        primary_type: Primary scam category key, or None.
    """
    if not text or not text.strip():
        return 0, [], [], None

    total_weight = 0
    reasons: List[str] = []
    spans: List[Tuple[int, int]] = []
    type_weights: Dict[str, int] = {}

    for pattern, weight, label, scam_type in RULES:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            total_weight += weight
            reasons.append(label)
            spans.extend([m.span() for m in matches])
            if scam_type:
                type_weights[scam_type] = type_weights.get(scam_type, 0) + weight

    score = min(100, total_weight)
    primary_type = max(type_weights, key=type_weights.get) if type_weights else None
    return score, reasons, spans, primary_type


def highlight(text: str, spans: List[Tuple[int, int]]) -> str:
    """Safely escapes HTML and marks matched spans with <mark> tags.

    Merges overlapping and adjacent spans to avoid malformed HTML.
    """
    if not text:
        return ""
    if not spans:
        return html.escape(text)

    # Sort and merge intervals
    merged: List[List[int]] = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])

    output: List[str] = []
    cursor = 0
    for start, end in merged:
        output.append(html.escape(text[cursor:start]))
        output.append(f"<mark>{html.escape(text[start:end])}</mark>")
        cursor = end
    output.append(html.escape(text[cursor:]))
    return "".join(output)


def complaint(
    text: str,
    score: int,
    primary_type: Optional[str],
    reasons: List[str],
    spans: List[Tuple[int, int]],
    lang_name: str,
) -> str:
    """Generates structured complaint helper text suitable for 1930 / cybercrime.gov.in."""
    phrases = sorted({text[a:b].strip().lower() for a, b in spans if text[a:b].strip()})
    type_label = TYPES[primary_type][0] if primary_type and primary_type in TYPES else "Suspicious / Unclassified Call"

    return (
        "SCAM CALL COMPLAINT SUMMARY\n"
        f"Date/Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
        f"Suspected Scam Type: {type_label}\n"
        f"Risk Score: {score}/100\n"
        f"Call Language: {lang_name}\n"
        f"Red Flags Detected: {', '.join(reasons) if reasons else 'None'}\n"
        f"Key Phrases Heard: {', '.join(phrases) if phrases else 'None'}\n"
        f"Transcript:\n{text.strip()}\n\n"
        "Official Action Recommended:\n"
        "- National Cyber Crime Reporting Portal: https://cybercrime.gov.in\n"
        "- Toll-Free Citizen Financial Cyber Fraud Helpline: 1930\n"
        "Suspect Caller Number: [Add caller ID / phone number here]"
    )

