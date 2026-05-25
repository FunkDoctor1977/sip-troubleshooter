# SIP Troubleshooter — Test Plan

Pre-flight checklist for exercising every analyzer scenario, every upload path, and every edge case before going live in front of a recruiter or hiring manager. **None of this requires an API key** — the v0.2 analyzer is fully rule-based.

## 0. Setup

| | |
|---|---|
| URL | http://localhost:8501 |
| Bundled text fixtures | [`fixtures/text/`](fixtures/text/) |
| Bundled pcap captures | [`fixtures/pcap/`](fixtures/pcap/) |

If the app isn't running:

```powershell
$env:PATH = "C:\Users\asims\anaconda3\Library\bin;" + $env:PATH
cd "C:\Users\asims\Build Lab test\sip-troubleshooter"
py -3.9 -m streamlit run app.py
```

---

## 1. Sidebar fixture selector

**Goal:** Verify the canned text fixtures load and classify correctly.

| # | Fixture | Expected scenario | Expected severity |
|---|---------|-------------------|-------------------|
| 1.1 | `01-basic-call-success.txt` | "Successful basic call (INVITE → 200 OK → ACK → BYE)" | 🟢 Healthy |
| 1.2 | `02-registration-with-auth.txt` | "REGISTER with 401 digest challenge (UA re-registered with credentials and was accepted)" | 🟢 Healthy |
| 1.3 | `03-call-486-busy-here.txt` | "486 Busy Here — callee occupied" | 🟡 Warning |
| 1.4 | `04-call-488-codec-mismatch.txt` | "488 Not Acceptable Here — SDP / codec negotiation failure" | 🔴 Error |
| 1.5 | `05-call-503-service-unavailable.txt` | "503 Service Unavailable — upstream cannot route the call" | 🔴 Error |
| 1.6 | `06-call-407-proxy-auth.txt` | "407 Proxy Authentication Required (call subsequently authenticated and completed)" | 🟢 Healthy |

For each: pick from the sidebar dropdown → trace populates the textarea → click **Analyze trace** → verify scenario, severity, summary, root cause, and next-steps all render.

**Watch for:** the *Next steps* list should reflect the specific scenario (e.g. 488 should mention codec policy alignment, 503 should mention checking the carrier status page). If next-steps are generic, the analyzer rule didn't match cleanly.

---

## 2. Text file upload

**Goal:** Verify drag-and-drop and Browse for plain-text traces.

| # | Step | Expected |
|---|------|----------|
| 2.1 | Save one of the bundled text fixtures to your desktop as `test.txt` | (Setup step) |
| 2.2 | Drag the file into the **"Drag and drop file here"** area in the main column | Green success banner: *"Loaded test.txt — N characters."* Caption above the textarea: *"📂 Uploaded file: test.txt (N bytes)"*. Textarea populated. |
| 2.3 | Click **Analyze trace** | Same diagnosis as in section 1. |
| 2.4 | Click **Browse files**, navigate to `fixtures/text/04-call-488-codec-mismatch.txt`, select it | Loaded successfully. |
| 2.5 | Try uploading a file with a `.log` or `.out` extension containing SIP text | Loaded successfully — the uploader accepts `.txt / .log / .out / .trace`. |

**Watch for:** if the upload shows an exclamation icon next to the filename, see the [README note on Streamlit XSRF](.streamlit/config.toml) — `.streamlit/config.toml` disables XSRF protection for local dev. If you've cloned fresh, make sure that file is present.

---

## 3. Binary pcap upload (the impressive bit)

**Goal:** Verify scapy decodes pcap captures into a usable text ladder and the analyzer classifies them.

| # | File | What it tests | Expected analyzer output |
|---|------|---------------|--------------------------|
| 3.1 | `fixtures/pcap/aaa.pcap` (111 KB) | 80 SIP messages, includes proxy-auth flow | "407 Proxy Authentication Required (call subsequently authenticated and completed)" |
| 3.2 | `fixtures/pcap/SIP_DTMF2.cap` (420 KB) | RFC 2833 DTMF call | "Successful basic call" or "INVITE observed with non-standard outcome" depending on the call structure |
| 3.3 | `fixtures/pcap/DTMFsipinfo.pcap` (25 KB) | SIP INFO DTMF call | "Successful basic call" |
| 3.4 | `fixtures/pcap/Asterisk_ZFONE_XLITE.pcap` (250 KB) | 702 SIP messages — full REGISTER + digest auth handshake | "REGISTER with 401 digest challenge (UA re-registered with credentials and was accepted)" |
| 3.5 | `fixtures/pcap/SIP_CALL_RTP_G711.pcap` (902 KB) | 364 SIP messages, multiple re-INVITEs | "INVITE observed with non-standard outcome" — this is correct behaviour: the v0.2 rules engine deliberately admits it doesn't have a pattern for multi-leg calls. **This is the demoable talking point for v0.3.** |
| 3.6 | `fixtures/pcap/metasploit-sip-invite-spoof.pcap` (<1 KB) | INVITE spoof flood from pentest | "INVITE observed with non-standard outcome" |

For each: upload via drag-and-drop or Browse → on first upload, watch the *Decoding…* spinner → success banner shows extracted message count → textarea fills with the decoded ladder → click Analyze.

**Watch for:**
- First pcap upload triggers a one-time scapy / libpcap-warning print on stderr — harmless, scapy uses its offline reader.
- Decode is truncated to the first 80 SIP messages by design (`max_messages` in `pcap_decoder.py`). Footer note in the decoded text confirms this when it kicks in.
- The "non-standard outcome" result on 3.5 and 3.6 is **not a bug** — talk it up as graceful degradation.

---

## 4. Manual paste

**Goal:** Verify the textarea takes pasted text directly without needing a file.

| # | Step | Expected |
|---|------|----------|
| 4.1 | Clear the trace textarea (or hit Reset / refresh) | Empty textarea, empty diagnosis panel. |
| 4.2 | Open any text fixture in Notepad, Ctrl+A → Ctrl+C, then paste into the textarea | Trace appears in the textarea. |
| 4.3 | Click **Analyze trace** | Same diagnosis as in section 1. |

---

## 5. Edge cases

| # | Scenario | Expected |
|---|----------|----------|
| 5.1 | Empty textarea, click Analyze | Scenario: "Empty input". Severity: 🟢. Next step: paste a trace or load a fixture. |
| 5.2 | Paste plain English ("hello, how are you") | Scenario: "Unrecognised input". Severity: 🟡. Next step prompts to verify SIP content. |
| 5.3 | Paste partial SIP (e.g. just an INVITE line, no responses) | Scenario: "INVITE observed with non-standard outcome". Severity: 🟡. Notes that the analyzer recognises a fixed scenario set; v0.3 will use an LLM. |
| 5.4 | Upload a file with a wrong extension renamed (e.g. an MP3 renamed `.pcap`) | scapy fails to parse → red error from the decoder. App stays stable. |
| 5.5 | Try uploading two files in quick succession | Second upload replaces the first cleanly. Caption updates. |

---

## 6. Pre-demo checklist

Run this just before sharing the URL with anyone:

- [ ] Fresh dev server (`streamlit run app.py`) — first analyze is fastest after a fresh boot.
- [ ] Verify a bundled fixture loads and analyzes cleanly (run test 1.4 — the 488 codec mismatch, it's the most demoable rule).
- [ ] Verify a pcap upload works (run test 3.1 — `aaa.pcap`).
- [ ] Glance at the right sidebar to confirm Diagnosis panel renders cleanly with summary, root cause, next steps, references.
- [ ] If you'll show GitHub, have https://github.com/FunkDoctor1977/sip-troubleshooter open in another tab.

## 7. What's deliberately not yet built (talk-through ammo)

When someone asks "why doesn't it do X?", these are the honest, prepared answers:

- **"It doesn't handle complex calls with hold / transfer / re-INVITE."** Correct — v0.2 is a deterministic rules engine with a finite scenario list. v0.3 swaps the rule core for a Claude API call so any pasted trace gets reasoned about. Roadmap is in the README.
- **"It doesn't show the SIP ladder visually."** Correct — v0.4 will use Mermaid sequence diagrams. The data is already structured for it inside `pcap_decoder.py`.
- **"It's all text-based — no live capture."** Intentional. Live capture needs root / Wireshark / a sniffer running on the same host as the SIP traffic. Out of scope for a portfolio prototype; trivial to add for a real deployment via tshark integration.
- **"What about MGCP / H.323 / proprietary CUCM SDL traces?"** Out of scope — SIP only. CUCM SDL traces in particular are customer-confidential and not publicly available for testing (see `docs/SOURCES.md`).
