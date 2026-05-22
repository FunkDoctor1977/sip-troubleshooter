# SIP / VoIP Binary Captures

Real-world packet captures pulled from the **Wireshark Wiki SampleCaptures** archive (https://wiki.wireshark.org/SampleCaptures), the long-standing public reference set of network protocol traces. These are binary `.pcap` / `.cap` files — open them in Wireshark, or decode to text with `tshark`.

## Files

| File | Source | Description |
|------|--------|-------------|
| `aaa.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/aaa.pcap) | SIP signalling + RTP media. Basic call example, ~111 KB. |
| `SIP_DTMF2.cap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/SIP_DTMF2.cap) | Call with RFC 2833 (telephone-event) DTMF tone signalling, ~420 KB. |
| `DTMFsipinfo.pcap` | [Wireshark SampleCaptures](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/DTMFsipinfo.pcap) | Call with DTMF delivered out-of-band via the SIP INFO method, ~25 KB. |

## Licensing

The Wireshark Wiki itself is licensed under **CC BY-SA 4.0**. Individual captures are contributed for free reuse as protocol references — see the SampleCaptures page for any contributor-specific notes per file.

## Converting to text for the analyzer

The SIP Troubleshooter analyzer (currently) consumes text-form SIP. To convert a pcap to a text ladder view:

```bash
# Full decode of every SIP message in the capture:
tshark -r aaa.pcap -V -Y sip

# Compact one-line-per-message summary:
tshark -r aaa.pcap -Y sip -T fields -e frame.time_relative -e ip.src -e ip.dst -e sip.Method -e sip.Status-Code -e sip.Status-Line
```

Save the output as `.txt` and paste into the analyzer, or load directly with a file picker in a future release.

## More captures

A wider list of sources (RFC text-form examples, SIPp scenarios, Kamailio docs, PacketLife.net) is in [../../docs/SOURCES.md](../../docs/SOURCES.md).
