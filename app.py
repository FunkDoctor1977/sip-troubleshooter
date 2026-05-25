"""SIP Troubleshooter — Streamlit UI (v0.2).

Paste a SIP trace, upload a file (text or pcap), or pick a bundled fixture.
The analyzer identifies the scenario, explains what's happening, flags the
likely root cause, and suggests next debug steps.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from analyzer import analyse
from pcap_decoder import decode_pcap_to_text

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "text"

TEXT_EXTENSIONS = {".txt", ".log", ".out", ".trace"}
PCAP_EXTENSIONS = {".pcap", ".pcapng", ".cap"}
ALL_EXTENSIONS = TEXT_EXTENSIONS | PCAP_EXTENSIONS


def _load_fixture_names() -> list[str]:
    if not FIXTURES_DIR.exists():
        return []
    return sorted(p.name for p in FIXTURES_DIR.iterdir() if p.suffix == ".txt" and p.name != "README.md")


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _decode_uploaded_bytes(name: str, data: bytes) -> tuple[str, str | None]:
    """Return (text, error_message_or_None)."""
    suffix = Path(name).suffix.lower()
    if suffix in TEXT_EXTENSIONS or not suffix:
        try:
            return data.decode("utf-8"), None
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace"), None
    if suffix in PCAP_EXTENSIONS:
        try:
            return decode_pcap_to_text(data), None
        except RuntimeError as e:
            return "", str(e)
        except ValueError as e:
            return "", str(e)
    return "", f"Unsupported file type: {suffix or '(no extension)'}"


SEVERITY_BADGE = {
    "info": ("🟢", "Healthy"),
    "warning": ("🟡", "Warning"),
    "error": ("🔴", "Error"),
}


st.set_page_config(
    page_title="SIP Troubleshooter — Asim AI Lab",
    page_icon="📞",
    layout="wide",
)

st.title("📞 SIP Troubleshooter")
st.caption("Asim AI Lab · An AI assistant for diagnosing SIP signalling faults · v0.2 prototype")

with st.sidebar:
    st.header("Load a bundled fixture")
    st.write("Quickly load one of the bundled SIP traces to see the analyzer in action.")
    fixtures = _load_fixture_names()
    if not fixtures:
        st.warning("No fixtures found under fixtures/text/.")
        selected = None
    else:
        selected = st.selectbox(
            "Available traces",
            options=["(choose a fixture)"] + fixtures,
            index=0,
        )
    st.markdown("---")
    st.markdown(
        "**About this prototype**  \n"
        "v0.2 supports drag-and-drop upload of text traces and binary pcap "
        "captures (decoded with scapy).  \n\n"
        "v0.3 will replace the rule-based analyzer with a single Anthropic "
        "Claude API call so any pasted trace can be diagnosed."
    )
    st.markdown(
        "[View on GitHub](https://github.com/FunkDoctor1977/sip-troubleshooter)"
    )

if "trace_text" not in st.session_state:
    st.session_state.trace_text = ""
if "trace_source" not in st.session_state:
    st.session_state.trace_source = ""

if selected and selected != "(choose a fixture)":
    if st.session_state.get("_last_loaded") != ("fixture", selected):
        st.session_state.trace_text = _read_fixture(selected)
        st.session_state.trace_source = f"Bundled fixture: {selected}"
        st.session_state._last_loaded = ("fixture", selected)

left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("Input")
    st.markdown(
        "Drop a SIP trace file below, paste a trace into the box, or pick a fixture from the sidebar. "
        "Supports plain-text traces (`.txt`, `.log`, `.out`, `.trace`) and binary captures "
        "(`.pcap`, `.pcapng`, `.cap`) — pcap files are decoded automatically and SIP messages "
        "extracted into a text ladder."
    )

    uploaded = st.file_uploader(
        "Upload a SIP trace",
        type=sorted(ext.lstrip(".") for ext in ALL_EXTENSIONS),
        accept_multiple_files=False,
    )

    if uploaded is not None:
        upload_key = ("upload", uploaded.name, uploaded.size)
        if st.session_state.get("_last_loaded") != upload_key:
            with st.spinner(f"Decoding {uploaded.name}…"):
                text_out, err = _decode_uploaded_bytes(uploaded.name, uploaded.getvalue())
            if err:
                st.error(err)
            else:
                st.session_state.trace_text = text_out
                st.session_state.trace_source = f"Uploaded file: {uploaded.name} ({uploaded.size:,} bytes)"
                st.session_state._last_loaded = upload_key
                st.success(f"Loaded {uploaded.name} — {len(text_out):,} characters.")

    if st.session_state.trace_source:
        st.caption(f"📂 {st.session_state.trace_source}")

    trace = st.text_area(
        "SIP trace",
        value=st.session_state.trace_text,
        height=480,
        label_visibility="collapsed",
        key="trace_input",
    )
    analyse_clicked = st.button("Analyze trace", type="primary")

with right:
    st.subheader("Diagnosis")
    if analyse_clicked:
        result = analyse(trace)
        badge_icon, badge_label = SEVERITY_BADGE.get(result.severity, ("⚪", result.severity))

        st.markdown(f"### {badge_icon} {result.scenario}")
        st.caption(f"Severity: **{badge_label}**")

        st.markdown("**Summary**")
        st.write(result.summary)

        st.markdown("**Likely root cause**")
        st.write(result.likely_root_cause)

        if result.next_steps:
            st.markdown("**Next steps**")
            for step in result.next_steps:
                st.markdown(f"- {step}")

        if result.references:
            st.markdown("**References**")
            for ref in result.references:
                st.markdown(f"- {ref}")
    else:
        st.info("Drop a file, paste a trace, or load a fixture, then click **Analyze trace**.")
