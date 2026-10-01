# Architecture Document — TechNova (Phase 1)

## 1. Overview

This document describes the network architecture for our Computer Networks Phase 1 project — a private network service platform built across 4 MacBooks on one local network. Our private domain is `app.technova.test`.

Request flow in one line: **Client → DNS query (Mac 1) → HTTPS request (Mac 2) → Backend A or B (Mac 3 / Mac 4)**

## 2. Machine Roles

| Machine | Role | What It Runs |
|---|---|---|
| Mac 1 | Private DNS Server | dnsmasq — resolves `app.technova.test` and `api.technova.test` to Mac 2's IP |
| Mac 2 | Edge / Reverse Proxy + Load Balancer | nginx — terminates HTTPS (TLS), load-balances requests across Backend A and Backend B |
| Mac 3 | Backend Server A | Simple REST API on port 3001, returns `X-Backend: A` |
| Mac 4 | Backend Server B | Simple REST API on port 3002, returns `X-Backend: B`, also used as a test client |

## 3. IP / Service Table

| Machine | Role | IP Address | Service | Port |
|---|---|---|---|---|
| Mac 1 | DNS Server | 10.7.17.84 | dnsmasq | 53 |
| Mac 2 | Edge / Load Balancer | 10.7.12.92 | nginx (HTTPS) | 8443 |
| Mac 3 | Backend A | 10.7.0.238 *(confirm which Mac this is)* | REST API | 3001 |
| Mac 4 | Backend B | 10.7.5.97 *(confirm which Mac this is)* | REST API | 3002 |

> Note: the two backend IPs above (10.7.0.238 and 10.7.5.97) were confirmed reachable via ping during Step 0, but need to be matched to whichever Mac is running Backend A vs Backend B — update this table once that's confirmed.

## 4. Topology Diagram

See `topology-diagram.png` for the visual diagram. All 4 Macs connect to the same local Wi-Fi network (college lab Wi-Fi / shared hotspot). Mac 2 is the only machine clients talk to directly — Mac 3 and Mac 4 are never contacted directly by a client, only by Mac 2's nginx reverse proxy.

```
                     ┌─────────────┐
                     │   Client    │
                     │ (any Mac)   │
                     └──────┬──────┘
                            │
              1. DNS query for app.technova.test
                            │
                            ▼
                     ┌─────────────┐
                     │    Mac 1    │
                     │ DNS Server  │
                     │ (dnsmasq)   │
                     └──────┬──────┘
                            │
              2. Returns Mac 2's IP (10.7.12.92)
                            │
                            ▼
                     ┌─────────────┐
                     │    Mac 2    │
                     │ Edge / nginx│
                     │ TLS + LB    │
                     └──────┬──────┘
                            │
              3. HTTPS request, load-balanced
                 (round-robin)
                 ┌──────────┴──────────┐
                 ▼                     ▼
          ┌─────────────┐      ┌─────────────┐
          │    Mac 3    │      │    Mac 4    │
          │  Backend A  │      │  Backend B  │
          │  port 3001  │      │  port 3002  │
          └─────────────┘      └─────────────┘
```

## 5. Request Flow, Step by Step

1. **DNS resolution**: the client runs `dig app.technova.test` or simply opens `https://app.technova.test:8443` in a browser. The request first asks Mac 1 (the DNS server) to resolve the name. Mac 1 returns Mac 2's IP address (`10.7.12.92`).
2. **TCP handshake**: the client opens a TCP connection to Mac 2 on port 8443 (SYN → SYN-ACK → ACK).
3. **TLS handshake**: Mac 2 presents its self-signed TLS certificate for `app.technova.test`. The client (having trusted this certificate in advance) completes the TLS handshake, encrypting the connection.
4. **HTTP request + load balancing**: the client's HTTPS request reaches nginx on Mac 2, which forwards it to either Mac 3 (Backend A) or Mac 4 (Backend B) using round-robin load balancing.
5. **Response**: the backend returns a JSON response with an `X-Backend` header identifying which backend served it, plus a `Cache-Control` header. Mac 2 relays this back to the client over the encrypted connection.

## 6. Why This Design

- **Single entry point (Mac 2)**: the client never needs to know Mac 3 or Mac 4's IP addresses — this mirrors how a real cloud load balancer or CDN edge node works.
- **Private DNS (Mac 1)**: demonstrates that DNS is just a name-to-IP directory, independent of the actual TCP/TLS/HTTP connection that follows.
- **Two backends with load balancing**: proves horizontal scaling and round-robin distribution, visible via the alternating `X-Backend` header.
- **TLS termination at the edge**: centralizes certificate management in one place (Mac 2) rather than on every backend.

## 7. Evidence

Packet-level evidence (DNS query/response, TCP three-way handshake, TLS handshake, HTTP headers, load-balancing proof) is captured via Wireshark and stored in `docs/evidence/`. Failure-mode testing (wrong DNS server, wrong DNS record, one/both backends down, wrong port) is documented separately in the failure-demos notes.
