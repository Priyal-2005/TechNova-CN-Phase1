# TechNova CN Project — Private Network Service Platform

## Team Members

- Priyal Sarda [2401010354] — DNS Admin (Mac 1) — Phase 2: Extensions D & E
- Anusha Prathapani [2401010344] — Edge Engineer (Mac 2) — Phase 2: Extension C
- Kashika Agarwal [2401010215] — Backend Dev A (Mac 3) — Phase 2: Extension B
- Vaishnavi Dhanai [2401010489] — Backend Dev B (Mac 4) — Phase 2: Extension A

## Architecture

Four machines, each with one role (unchanged across both phases):

- **Mac 1**: Private DNS server (dnsmasq)
- **Mac 2**: Edge — nginx reverse proxy, TLS termination, load balancing
- **Mac 3**: Backend A — REST API on port 3001
- **Mac 4**: Backend B — REST API on port 3002

Request flow: Client → DNS query (Mac 1) → HTTPS request (Mac 2) → Backend A or B (Mac 3/4)

## Repository Structure

```
.
├── phase-1/              Phase 1 — Build & Observe
│   ├── backend-a/         Backend A source (Mac 3)
│   ├── backend-b/         Backend B source (Mac 4)
│   ├── certs/             Public TLS certificate (private key not committed)
│   ├── dnsmasq/           Mac 1 DNS config
│   ├── nginx/             Mac 2 edge/load-balancer config
│   └── docs/              Architecture doc, topology diagram, failure demos, Wireshark evidence
│
└── phase-2/              Phase 2 — Harden, Recover & Troubleshoot
    ├── dnsmasq-backup/     Extension A — backup DNS resolver config (Vaishnavi)
    ├── nginx-standby/      Extension E — standby edge config for DNS-based cutover (Priyal)
    ├── firewall/           Extension C — backend port isolation rules + rollback (Anusha)
    └── docs/               Phase 2 task guide + evidence folder
```

## Phase 1 — Build & Observe

### Documentation & Evidence

- **Architecture:** [`phase-1/docs/topology-diagram.png`](phase-1/docs/topology-diagram.png) and [`phase-1/docs/architecture.md`](phase-1/docs/architecture.md)
- **Failure Demonstrations:** [`phase-1/docs/Failures/failure-demos.md`](phase-1/docs/Failures/failure-demos.md)
- **Wireshark Evidence:** [`phase-1/docs/wireshark-evidence/`](phase-1/docs/wireshark-evidence/)

### How to Run the Backends

**Backend A (port 3001):**

    cd phase-1/backend-a
    python3 app.py

Test:

    curl -i http://localhost:3001/api/status

Expected: `X-Backend: A`, `Cache-Control: max-age=60`, `{"backend": "A", "status": "ok"}`

**Backend B (port 3002):**

    cd phase-1/backend-b
    python3 app.py

Test:

    curl http://localhost:3002/api/status

Both backends bind to `0.0.0.0` so other machines on the LAN can reach them.

### DNS Setup (dnsmasq — Mac 1)

Config: [`phase-1/dnsmasq/dnsmasq.conf`](phase-1/dnsmasq/dnsmasq.conf)

    brew install dnsmasq
    cp phase-1/dnsmasq/dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf
    sudo brew services start dnsmasq

### Edge / Load Balancer Setup (nginx — Mac 2)

Config: [`phase-1/nginx/nginx.conf`](phase-1/nginx/nginx.conf)
Certificate: [`phase-1/certs/app.technova.test.crt`](phase-1/certs/app.technova.test.crt) (public cert only — private key is not committed)

    brew install nginx
    cp phase-1/nginx/nginx.conf /opt/homebrew/etc/nginx/nginx.conf
    brew services start nginx

## Phase 2 — Harden, Recover & Troubleshoot

Phase 2 extends the same network above — nothing is rebuilt from scratch. The goal is resilience: the system should keep working, or fail cleanly and diagnosably, when something breaks.

**Full task breakdown:**

| Extension | Owner | What it proves |
|---|---|---|
| A — Backup DNS Resolver | Vaishnavi | DNS has no single point of failure |
| B — DNS TTL & Controlled Record Change | Kashika | Client-side caching behavior under TTL |
| C — Service Isolation (Backend Firewall Rules) | Anusha | Clients can't bypass the edge |
| D — High-Availability Failover | Priyal | Load balancer survives a dead backend |
| E — Controlled Edge Migration (DNS Cutover) | Priyal | Edge can be moved without new hardware |
| F — Faculty-Injected Troubleshooting Challenge | Everyone | Live, systematic fault diagnosis |

**Evidence:** [`phase-2/docs/evidence/`](phase-2/docs/evidence/)

### Key changes from Phase 1

- `nginx.conf`'s `upstream backend_pool` now includes `max_fails=2 fail_timeout=10s` on each server, so a dead backend is marked down quickly instead of stalling every request for 60 seconds (Phase 1 Test 3's documented gap).
- `dnsmasq.conf` now sets `local-ttl=60` for short, observable DNS caching. (`local-ttl=30` was tried first; macOS's resolver did not reliably auto-expire the cache at 30 seconds, so it was raised to 60 seconds.)
