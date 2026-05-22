"""SIP Troubleshooter — Streamlit UI (v0.1).

Paste a SIP trace and the analyzer identifies the scenario, explains what is
happening, flags the likely root cause, and suggests next debug steps.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from analyzer import analyse

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "text"


def _load_fixture_names() -> list[str]:
    if not FIXTURES_DIR.exists():
        return []
    return sorted(p.name for p in FIXTURES_DIR.iterdir() if p.suffix == ".txt" and p.name != "README.md")


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


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
st.caption("Asim AI Lab · An AI assistant for diagnosing SIP signalling faults · v0.1 prototype")

with st.sidebar:
    st.header("Load a fixture")
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
        "v0.1 uses a rule-based analyzer with handwritten diagnoses for the common "
        "scenarios shown in the fixtures.  \n\n"
        "v0.2 will replace the analyzer body with a single Anthropic Claude API call "
        "so any pasted trace can be diagnosed."
    )
    st.markdown(
        "[View on GitHub](https://github.com/FunkDoctor1977/sip-troubleshooter)"
    )

if "trace_text" not in st.session_state:
    st.session_state.trace_text = ""

if selected and selected != "(choose a fixture)":
    if st.session_state.get("_last_loaded") != selected:
        st.session_state.trace_text = _read_fixture(selected)
        st.session_state._last_loaded = selected

left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("SIP trace")
    trace = st.text_area(
        "Paste a SIP trace here, or pick a fixture from the sidebar.",
        value=st.session_state.trace_text,
        height=520,
        label_visibility="collapsed",
        key="trace_input",
    )
    analyse_clicked = st.button("Analyze trace", type="primary")

with right:
    st.subheader("Diagnosis")
    if analyse_clicked or (trace and st.session_state.get("auto_run")):
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
        st.info("Paste a trace or load a fixture, then click **Analyze trace**.")
