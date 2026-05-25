# SIP Troubleshooter

**An Asim AI Lab project** · An AI assistant for diagnosing SIP signalling faults.

## What it does

Paste in a SIP trace, ladder diagram, or Cisco UC log. The assistant:

1. **Parses the trace** — extracts the call flow, codecs, and response codes.
2. **Explains in plain English** — what is happening, in what order, between which endpoints.
3. **Flags the likely failure point** — which leg failed, which response code suggests which root cause.
4. **Suggests next debug steps** — concrete checks to run on the carrier, SBC, or PBX side.

Aimed at second/third-line UC engineers and pre-sales consultants who need to triage a SIP fault quickly without trawling through hundreds of lines of trace.

## Why this project

After more than a decade troubleshooting SIP-based unified communications across Cisco, Vodafone, BT, and Telefónica Tech, the diagnostic pattern is repeatable: read the ladder, find where the dialogue breaks, map the response code to a likely cause, propose a check. This prototype encodes that pattern in an LLM-based assistant so the slow, manual triage becomes a 30-second first pass.

A deliberate **prototype** demonstrating an AI use case where deep telecoms domain expertise — not generic AI — is the differentiator.

## Status

🚧 v0.1 in progress · README-first scaffold.

## Roadmap

- [x] v0.1 — Streamlit UI with paste-and-analyse flow
- [x] v0.2 — Drag-and-drop upload for text traces *and* binary pcap captures (decoded with scapy)
- [ ] v0.3 — Replace rule-based analyzer with live Claude API call for any pasted trace
- [ ] v0.4 — **SIP ladder diagram** — Wireshark-style sequence visualisation of the parsed call flow, rendered via Mermaid sequenceDiagram (colour-coded 1xx / 2xx / 4xx / 5xx, hover for full message)
- [ ] v0.5 — Failure-pattern playbook grounded in real-world UK carrier behaviour (Gamma, Colt, BT)
- [ ] v0.6 — Deploy to Streamlit Cloud · embed screenshots in this README

## Stack

Python · Streamlit · Anthropic Claude API

## Author

Asim Shahzad · [LinkedIn](https://linkedin.com/in/asim-shahzad-82183b2) · Birmingham, UK
