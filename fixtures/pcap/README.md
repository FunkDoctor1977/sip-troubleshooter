# SIP / VoIP Binary Captures

Real-world packet captures pulled from the **Wireshark Wiki SampleCaptures** archive (https://wiki.wireshark.org/SampleCaptures), the long-standing public reference set of network protocol traces. These are binary `.pcap` / `.cap` files — open them in Wireshark, or upload them straight into the SIP Troubleshooter (it decodes them on the fly with `scapy`).

## Files

| File | Source | Description | Approx. size |
|------|--------|-------------|--------------|
| `aaa.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/aaa.pcap) | SIP signalling + RTP media. Basic call example with proxy auth flow. | 111 KB |
| `SIP_DTMF2.cap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/SIP_DTMF2.cap) | Call with RFC 2833 (telephone-event) DTMF tone signalling. | 420 KB |
| `DTMFsipinfo.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/DTMFsipinfo.pcap) | Call with DTMF delivered out-of-band via the SIP INFO method. | 25 KB |
| `SIP_CALL_RTP_G711.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/SIP_CALL_RTP_G711) | Full call with G.711 codec, multiple legs and re-INVITEs — good stress test for the analyzer. | 902 KB |
| `Asterisk_ZFONE_XLITE.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/Asterisk_ZFONE_XLITE.pcap) | Asterisk PBX talking to an X-Lite softphone with ZRTP-secured media; includes a full registration handshake with digest auth. | 250 KB |
| `metasploit-sip-invite-spoof.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/metasploit-sip-invite-spoof.pcap) | Spoofed INVITE flood from a pentest tool — useful as a "what does abnormal SIP traffic look like" reference. | <1 KB |

## A note on CUCM / Call Manager traces

Genuine Cisco Unified Communications Manager **SDL traces** (Cisco's proprietary call-processing debug format) are typically customer-confidential and not published publicly by Cisco. What this fixture set contains instead is **SIP signalling captured on the wire** — the same signalling that CUCM, CUBE, ISR-SBC, and other Cisco call agents emit and receive. The analyzer consumes SIP messages, not SDL events, so wire-captured pcaps are the directly relevant artefact.

If you have an anonymised customer trace you want to drop in for testing, the upload box in the Streamlit app accepts `.pcap`, `.pcapng`, and `.cap` directly.

## Licensing

The Wireshark Wiki itself is licensed under **CC BY-SA 4.0**. Individual captures are contributed for free reuse as protocol references — see the SampleCaptures page for any contributor-specific notes per file.

## Converting to text for the analyzer

The SIP Troubleshooter decodes uploaded pcaps automatically. If you want to convert a pcap to a text ladder view yourself for inspection:

```bash
# Full decode of every SIP message in the capture:
tshark -r aaa.pcap -V -Y sip

# Compact one-line-per-message summary:
tshark -r aaa.pcap -Y sip -T fields -e frame.time_relative -e ip.src -e ip.dst -e sip.Method -e sip.Status-Code -e sip.Status-Line
```

## More sources

A wider list (RFC text-form examples, SIPp scenarios, Kamailio docs, PacketLife.net) lives in [../../docs/SOURCES.md](../../docs/SOURCES.md).
