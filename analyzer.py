"""Mocked SIP trace analyzer for v0.1.

This module pattern-matches against the structural signals in a pasted SIP
trace and returns a structured diagnosis. In v0.2 the body of analyse() will
be replaced by a single call to the Anthropic Claude API; the dataclass shape
returned to the UI stays identical so the front-end does not change.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class Analysis:
    scenario: str
    summary: str
    likely_root_cause: str
    severity: str  # "info" | "warning" | "error"
    next_steps: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


def _has(trace: str, pattern: str) -> bool:
    return re.search(pattern, trace, re.IGNORECASE | re.MULTILINE) is not None


def _count(trace: str, pattern: str) -> int:
    return len(re.findall(pattern, trace, re.IGNORECASE | re.MULTILINE))


def analyse(trace: str) -> Analysis:
    """Identify the scenario in a pasted SIP trace and return a diagnosis."""
    t = trace.strip()
    if not t:
        return Analysis(
            scenario="Empty input",
            summary="No SIP messages were detected in the input.",
            likely_root_cause="Empty trace.",
            severity="info",
            next_steps=["Paste a SIP trace into the input box, or load one of the bundled fixtures from the sidebar."],
        )

    # 488 Not Acceptable Here — codec mismatch
    if _has(t, r"^SIP/2\.0 488"):
        offers_g729_only = _has(t, r"m=audio \S+ RTP/AVP 18\b") and not _has(t, r"m=audio \S+ RTP/AVP \S*\b0\b")
        return Analysis(
            scenario="488 Not Acceptable Here — SDP / codec negotiation failure",
            summary=(
                "The callee rejected the INVITE with 488 Not Acceptable Here. This response is sent when "
                "the offered SDP media format(s) cannot be matched to anything the callee supports. "
                + ("The offer contains only G.729 (payload 18), which the callee did not accept." if offers_g729_only else "")
            ),
            likely_root_cause=(
                "Codec policy mismatch between the two legs. The caller's allowed codec list does not "
                "intersect with the callee's allowed list — most commonly G.729-only on one side and "
                "G.711 (PCMU/PCMA) only on the other."
            ),
            severity="error",
            next_steps=[
                "Check the codec list configured on the caller PBX / SBC against the codec list permitted on the carrier or callee side.",
                "If transcoding is allowed, enable it on the SBC between the two legs.",
                "If transcoding is not allowed, align both sides on a common codec (typically G.711 PCMU or PCMA for UK trunking).",
                "Inspect the Warning header on the 488 — RFC 3261 defines code 304 'Incompatible media format' as the standard reason.",
            ],
            references=["RFC 3261 §21.4.26 (488 Not Acceptable Here)", "RFC 3264 (Offer/Answer)"],
        )

    # 486 Busy Here
    if _has(t, r"^SIP/2\.0 486"):
        return Analysis(
            scenario="486 Busy Here — callee occupied",
            summary="The callee's UA explicitly rejected the INVITE with 486 Busy Here.",
            likely_root_cause=(
                "Callee is already in an active call dialogue, has DND enabled, or has reached its "
                "configured maximum number of concurrent sessions."
            ),
            severity="warning",
            next_steps=[
                "Confirm whether the callee is genuinely on another call at the time of the trace.",
                "Check the line/device configuration for DND and busy-trigger thresholds.",
                "If this is a hunt-group destination, check the group's configured busy treatment (overflow, voicemail, busy-tone).",
            ],
            references=["RFC 3261 §21.4.24 (486 Busy Here)"],
        )

    # 503 Service Unavailable
    if _has(t, r"^SIP/2\.0 503"):
        retry_after = re.search(r"^Retry-After:\s*(\d+)", t, re.IGNORECASE | re.MULTILINE)
        return Analysis(
            scenario="503 Service Unavailable — upstream cannot route the call",
            summary=(
                "The next-hop SBC / carrier proxy returned 503 Service Unavailable. "
                + (f"It indicated a retry after {retry_after.group(1)} seconds." if retry_after else "")
            ),
            likely_root_cause=(
                "Upstream is unable to process the request right now. Common drivers: planned maintenance "
                "on the trunk, capacity exhaustion on the route, downstream destination unreachable, or "
                "trunk in administratively-disabled state."
            ),
            severity="error",
            next_steps=[
                "Check the carrier's status page for any open incident or planned maintenance window.",
                "Verify CDR / billing platform for trunk capacity utilisation immediately before the trace.",
                "Confirm the destination prefix is provisioned on the trunk and that DDI routing is correct.",
                "If 503 includes Retry-After, ensure the PBX honours it before retrying to avoid being throttled.",
            ],
            references=["RFC 3261 §21.5.4 (503 Service Unavailable)"],
        )

    # 407 Proxy Authentication Required (often part of a successful retry)
    if _has(t, r"^SIP/2\.0 407"):
        completed = _has(t, r"^SIP/2\.0 200 OK") and _has(t, r"^Proxy-Authorization:")
        return Analysis(
            scenario=(
                "407 Proxy Authentication Required — digest challenge"
                + (" (call subsequently authenticated and completed)" if completed else " (no successful re-INVITE observed)")
            ),
            summary=(
                "The carrier proxy challenged the INVITE with 407 Proxy Authentication Required, requesting "
                "HTTP Digest credentials. "
                + (
                    "The PBX subsequently re-issued the INVITE with a Proxy-Authorization header and the call "
                    "reached 200 OK — this trace shows normal authenticated-trunk behaviour."
                    if completed
                    else "No subsequent INVITE with Proxy-Authorization is present in the trace — the call did not progress."
                )
            ),
            likely_root_cause=(
                "Trunk requires per-call digest authentication. Either expected (working trunk) or "
                "the PBX is not configured with the correct trunk credentials, in which case the retry "
                "either does not happen or also fails."
            ),
            severity="info" if completed else "error",
            next_steps=(
                [
                    "Nothing to do — this is expected behaviour for a digest-authenticated SIP trunk.",
                    "If you are seeing 407s on a trunk that should be IP-whitelist authenticated, verify the trunk profile on the carrier side.",
                ]
                if completed
                else [
                    "Check that the PBX is configured with valid trunk credentials (username, password, realm).",
                    "Verify the realm in the 407 challenge matches what is configured on the PBX.",
                    "Check time synchronisation on the PBX — large clock drift can invalidate nonce calculations on some carriers.",
                    "Confirm with the carrier that the trunk account is not locked or expired.",
                ]
            ),
            references=["RFC 3261 §22 (Usage of HTTP Authentication)"],
        )

    # 401 Unauthorized during REGISTER
    if _has(t, r"^SIP/2\.0 401") and _has(t, r"^REGISTER\b"):
        registered = _count(t, r"^SIP/2\.0 200 OK") >= 1 and _has(t, r"^Authorization:")
        return Analysis(
            scenario=(
                "REGISTER with 401 digest challenge"
                + (" (UA re-registered with credentials and was accepted)" if registered else " (no successful re-registration observed)")
            ),
            summary=(
                "The registrar challenged the initial REGISTER with 401 Unauthorized. "
                + (
                    "The UA re-submitted REGISTER with an Authorization header and was accepted with 200 OK."
                    if registered
                    else "No re-REGISTER with credentials succeeded in this trace."
                )
            ),
            likely_root_cause=(
                "Standard digest registration handshake — this is expected for any registrar that requires "
                "authentication."
                if registered
                else "UA failed to complete the digest challenge: bad credentials, realm mismatch, nonce expiry, or the UA never retried."
            ),
            severity="info" if registered else "error",
            next_steps=(
                [
                    "Nothing to do — this is normal registration behaviour.",
                ]
                if registered
                else [
                    "Verify the SIP username and password configured on the UA.",
                    "Verify the realm in the 401 WWW-Authenticate challenge matches the realm configured on the UA.",
                    "Check the UA logs for retry behaviour — some endpoints back off after repeated failures.",
                    "Check time sync — significant clock drift can invalidate nonces on strict registrars.",
                ]
            ),
            references=["RFC 3261 §22", "RFC 3261 §10 (Registrations)"],
        )

    # Successful basic call: INVITE -> 200 OK -> ACK -> BYE -> 200
    if (
        _has(t, r"^INVITE\b")
        and _has(t, r"^SIP/2\.0 200 OK")
        and _has(t, r"^ACK\b")
        and _has(t, r"^BYE\b")
    ):
        return Analysis(
            scenario="Successful basic call (INVITE → 200 OK → ACK → BYE)",
            summary=(
                "A complete, successful SIP dialogue is present: INVITE is answered with 200 OK, "
                "ACK confirms the dialogue, media flows, and BYE terminates the call cleanly with 200 OK."
            ),
            likely_root_cause="No fault — this is a healthy call flow.",
            severity="info",
            next_steps=[
                "If you uploaded this expecting a fault, check the call ID and timestamps against the customer's reported issue — you may be looking at a different call.",
                "Inspect the SDP in the 200 OK to confirm the negotiated codec matches expectations.",
            ],
            references=["RFC 3261 §17 (Transactions)"],
        )

    # Generic INVITE present but unclear outcome
    if _has(t, r"^INVITE\b"):
        responses = re.findall(r"^SIP/2\.0 (\d{3})", t, re.MULTILINE)
        return Analysis(
            scenario="INVITE observed with non-standard outcome",
            summary=(
                "An INVITE is present in the trace but the outcome does not match a recognised scenario. "
                f"Final response codes seen: {', '.join(sorted(set(responses))) or '(none)'}."
            ),
            likely_root_cause="Cannot determine without deeper inspection. v0.1 of the analyzer recognises a fixed set of scenarios.",
            severity="warning",
            next_steps=[
                "Check Wireshark / VoIP analyzer for the full ladder diagram.",
                "Look at the final response code and consult RFC 3261 §21 for its meaning.",
                "If this is a recurring pattern, capture multiple examples — v0.2 of this analyzer will use an LLM to handle novel scenarios.",
            ],
            references=["RFC 3261 §21 (Response Codes)"],
        )

    return Analysis(
        scenario="Unrecognised input",
        summary="No SIP request methods or status lines were detected.",
        likely_root_cause="Input does not appear to be a SIP trace.",
        severity="warning",
        next_steps=[
            "Verify you have pasted SIP signalling, not RTP media or a different protocol.",
            "Try one of the bundled fixtures from the sidebar to see the expected input format.",
        ],
    )
