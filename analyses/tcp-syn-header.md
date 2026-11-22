# Analysis: TCP SYN Header

**Type:** Packet analysis practice

## The evidence

```
Source: 46822          Destination: 443
Sequence: 0            Acknowledgement Number: 0
Data offset: 40 bytes  Flags: 0x002 (SYN)
Window size: 64240     Checksum: 0x58a9
Urgent pointer: 0      Options: Max segment size, Timestamps
```

## Assessment

This is the **first segment of a TCP three-way handshake**: a client opening a connection to an HTTPS service.

## Field-by-field

| Field | Inference |
|---|---|
| Src port 46822 | An ephemeral port the client's OS picked, so the sender is almost certainly the client. |
| Dst port 443 | HTTPS/TLS. The client is probably reaching a secure web service. |
| Seq 0 / Ack 0 | Probably relative numbers (Wireshark's default). A real initial sequence number is a random 32-bit value. In a raw capture, a literal 0 could suggest a crafted packet from a tool like hping or Scapy. |
| Data offset 40 bytes | 20 bytes of fixed header plus 20 bytes of options. MSS and Timestamps account for 14, so the rest is padding or options not shown (often SACK-permitted and Window Scale). |
| Flags 0x002 | SYN only. It's an opening request, not a SYN-ACK, and no data has been exchanged yet. |
| Window 64240 | 44 × 1460, a common initial window in modern Windows and Linux stacks. It hints at the OS family but doesn't identify it. |
| MSS + Timestamps | MSS is typically 1460 on Ethernet. Timestamps (RFC 7323) mean a modern stack. |
| Checksum | Can't be verified without the IP pseudo-header and the payload. |
| Urgent pointer 0 | Expected, since URG isn't set. |

## What this header can't tell you

The IP addresses, whether a SYN-ACK came back, whether the handshake completed, what TLS traffic followed, or whether the sender is legitimate. One SYN with normal options looks like ordinary browsing, but scanners and crafted traffic can look the same. Judging intent takes the IP header and the surrounding flow.

## Skills demonstrated

TCP/IP header analysis, OS fingerprinting cues, and spotting crafted packets.
