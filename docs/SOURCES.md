# SIP Test Fixture Sources

A working list of public, freely-redistributable sources of SIP traces and signalling examples for use as test fixtures in this project.

> Compiled from established knowledge of long-standing public resources. Verify each URL and licence at the point of download before bundling anything into this repository.

## Recommended sources (download priority order)

### 1. IETF RFCs — text-form call flow examples *(start here)*
- **RFC 3665** — SIP Basic Call Flow Examples · https://www.rfc-editor.org/rfc/rfc3665
- **RFC 3666** — SIP PSTN Call Flows
- **RFC 5359** — SIP Service Examples (extends 3665)
- **Contents:** Full text-form SIP messages for successful registration, successful session, session with authentication, unsuccessful (busy, no answer, request failure).
- **Licence:** IETF Trust Legal Provisions — text may be reproduced verbatim.
- **Format:** Plain text — directly usable as LLM input.

### 2. SIPp project — scenario XML files
- **Repo:** https://github.com/SIPp/sipp
- **Contents:** Text-form SIP message templates for UAC/UAS, registration, 3PCC, auth challenges. Default scenarios (`uac.xml`, `uas.xml`, `branchc.xml`, `regexp.xml`, `3pcc-*.xml`).
- **Licence:** GPLv2+ — freely redistributable with attribution.
- **Use:** Easily mutated to produce 401 / 403 / 486 / 487 / 503 variants.

### 3. Wireshark Wiki — SampleCaptures
- **URL:** https://wiki.wireshark.org/SampleCaptures (SIP / VoIP section)
- **Contents:** `sip.pcap`, `sip_REGISTER.pcap`, `aaa.pcap`, `metasploit-sip-invite-spoof.pcap`, plus RTP-paired captures.
- **Licence:** Page CC-BY-SA; individual captures per contributor — check per-file.
- **Format:** Binary pcap — use `tshark -V <file>.pcap` to convert to a text ladder view that the LLM can consume.

### 4. PacketLife.net — VoIP captures library
- **URL:** https://packetlife.net/captures/category/voip/
- **Contents:** Curated VoIP/SIP captures including SIP registration and call setup.
- **Licence:** CC-BY-SA 3.0 — redistributable with attribution.

### 5. Kamailio documentation
- **URL:** https://www.kamailio.org/wikidocs/
- **Contents:** Annotated SIP flows for registration, digest auth (401/407), failure routes (503), trunk auth.
- **Licence:** Docs are GPL-compatible; example traces in docs reusable.

### 6. GitHub — community SIP test corpora
- **Search terms:** `topic:sip pcap`, `topic:sipp`, `voip-patrol`, `sipvicious` test fixtures.
- **Notable repos:** `SIPp/sipp`, `EnableSecurity/sipvicious` (includes malformed and auth-failure traffic).
- **Licence:** Per-repo — most are GPL/BSD/MIT and redistributable. Always check `LICENSE` before bundling.

## Likely dead-ends / use with caution

- **Vendor docs (Cisco / Avaya / Mitel)** — ladder diagrams embedded in copyrighted PDFs. Reference and link only; do not bundle.
- **Cloudshark public captures** (https://www.cloudshark.org/) — per-upload licence; treat as link-only unless the uploader has stated terms.
- **Asterisk mailing list pastes / Pastebin / Gist hits** — real-world but no blanket licence. Reference only.
- **Old `sipp.sourceforge.net` URLs** — project has moved to GitHub; many SourceForge URLs now redirect or 404.

## Repo layout strategy

Prioritise **text-form sources** (RFCs, SIPp XML, Kamailio docs) for the in-repo fixture set under `fixtures/text/` — these feed the LLM directly.

Keep binary pcaps separately under `fixtures/pcap/` with a `tshark`-based conversion script that generates matching ladder-view `.txt` files. This preserves the original capture for Wireshark validation while giving the LLM clean text input.
