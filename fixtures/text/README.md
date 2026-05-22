# SIP Test Fixtures

A small library of text-form SIP call flow examples for testing the SIP Troubleshooter. Each file follows the standard "ladder" convention used in IETF call-flow documents and Cisco/Asterisk TAC examples — message direction is implied by the order of messages between two parties (e.g. Alice → Proxy → Bob).

## Provenance

These are **protocol-accurate, textbook SIP examples** following the conventions in:

- **RFC 3261** — SIP: Session Initiation Protocol
- **RFC 3665** — SIP Basic Call Flow Examples
- **RFC 3666** — SIP PSTN Call Flow Examples
- **RFC 5359** — SIP Service Examples
- **RFC 3550** — RTP (referenced by SDP)
- **RFC 3261 §22** — HTTP Digest authentication as used in SIP

Headers and behaviour conform to RFC 3261. They are written from protocol knowledge, not copied verbatim from any single source; the message structure is dictated by the RFC.

Identifiers (Call-IDs, branches, tags) are illustrative — they follow the format required by the RFC but do not correspond to any real call.

## Files

| # | File | Scenario |
|---|------|----------|
| 01 | `01-basic-call-success.txt` | Successful basic call: INVITE → 100 → 180 → 200 → ACK → BYE → 200 |
| 02 | `02-registration-with-auth.txt` | Endpoint registration with digest auth: REGISTER → 401 → REGISTER+credentials → 200 |
| 03 | `03-call-486-busy-here.txt` | Called party busy: INVITE → 100 → 486 Busy Here → ACK |
| 04 | `04-call-488-codec-mismatch.txt` | SDP negotiation failure (G.729 only on caller, G.711 only on callee): INVITE → 488 Not Acceptable Here → ACK |
| 05 | `05-call-503-service-unavailable.txt` | Carrier/SBC outage: INVITE → 503 Service Unavailable → ACK |
| 06 | `06-call-407-proxy-auth.txt` | Trunk proxy authentication challenge: INVITE → 407 Proxy Authentication Required → ACK → INVITE+credentials → 200 → ACK |

## Usage

Open the SIP Troubleshooter (`streamlit run app.py`), paste the contents of any file into the input box, and click **Analyze**. The analyzer will identify the scenario, explain what is happening, flag the likely root cause, and suggest next debug steps.
