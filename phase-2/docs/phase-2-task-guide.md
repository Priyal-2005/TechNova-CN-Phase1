# CN Project — Phase 2 Task Guide (Team TechNova)

Phase 2 extends the same network from Phase 1 — nothing gets rebuilt from scratch. The goal this phase is resilience: the system should keep working (or fail cleanly and diagnosably) when something breaks.

**Machines (unchanged from Phase 1):**
Mac 1 = Priyal = Private DNS · Mac 2 = Anusha = Edge/nginx · Mac 3 = Kashika = Backend A · Mac 4 = Vaishnavi = Backend B / test client.

**Role ownership this phase:**

| Owner | Extension(s) |
|---|---|
| Priyal | D — HA Failover, E — Controlled Edge Migration |
| Kashika | B — DNS TTL & Controlled Record Change (+ assists A) |
| Vaishnavi | A — Backup DNS Resolver |
| Anusha | C — Service Isolation (Backend Firewall Rules) |
| Everyone | F — Faculty-Injected Troubleshooting Challenge |

---

## Extension A — Backup DNS Resolver
**Owner: Vaishnavi (Mac 4)**

### A.1 — Install and configure a second dnsmasq instance
**What:** On Mac 4, install dnsmasq and add the same DNS records Mac 1 has.
**Why:** A single DNS server is a single point of failure.
**Expected result:** `dig @<Mac4_IP> app.technova.test` resolves correctly, independent of Mac 1.

### A.2 — Point client Macs at both DNS servers
**What:** Add Mac 1's IP as primary and Mac 4's IP as secondary on at least two client Macs.
**Why:** macOS falls through to the next listed resolver automatically.
**Expected result:** Normal queries still succeed through Mac 1.

### A.3 — Demonstrate failover
**What:** Stop dnsmasq on Mac 1, then query from a client.
**Why:** Proves the backup is live, not just configured.
**Expected result:** Resolution continues via Mac 4.

### A.4 — Explain the distinction
**What:** Explain DNS service failure vs. application server failure.
**Why:** Tests that you understand these are independent layers.

---

## Extension B — DNS TTL and Controlled Record Change
**Owner: Kashika (Mac 3, coordinating with Priyal on Mac 1)**

### B.1 — Set a short, visible TTL
**What:** Add `local-ttl=60` to the dnsmasq config on Mac 1.
**Why:** Makes the cache-then-expire cycle observable in a short demo.
**Note:** `local-ttl=30` was tried first; macOS's resolver did not reliably auto-expire at 30s, so the TTL was raised to 60s, which worked correctly.

### B.2 — Resolve, then change the record while a client holds the cached answer
**What:** Resolve once, then change the record without flushing.
**Why:** Demonstrates caching is a real behavioral effect.
**Expected result:** Client still shows the old IP within the TTL window.
**Note:** Test with `ping`/`curl`, not `dig`/`nslookup` — those bypass the client cache entirely.

### B.3 — Show the cache expiring
**What:** Wait past the TTL window, re-run without flushing.
**Expected result:** New IP appears automatically. (Confirmed working at 60s.)

### B.4 — Demonstrate a manual flush too
**What:** `sudo dscacheutil -flushcache` immediately after a record change.
**Expected result:** New IP appears immediately.

### B.5 — Explain the production parallel
**What:** Connect this to real-world DNS-based traffic cutover.

---

## Extension C — Service Isolation (Backend Firewall Rules)
**Owner: Anusha (Mac 2)**

### C.1 — Restrict direct access to backend ports
**What:** Firewall rules so ports 3001/3002 only accept connections from Mac 2.
**Expected result:** A client Mac (not Mac 2) is refused/times out hitting a backend directly.

### C.2 — Confirm the edge is unaffected
**What:** Confirm Mac 2 can still reach both backends, and the full HTTPS path still works.

### C.3 — Keep a rollback
**What:** Save the firewall rules before/after, restore once evidence is captured.

---

## Extension D — High-Availability Failover Behavior
**Owner: Priyal**

### D.1 — Confirm no health checks are currently configured
**What:** Review Mac 2's nginx `upstream` block.
**Expected result:** Confirmed — no `max_fails`/`fail_timeout` present (same gap flagged in Phase 1 Test 3).

### D.2 — Add failure detection to nginx
**What:** Add `max_fails=2 fail_timeout=10s` to each server line in `upstream backend_pool`, reload nginx.
**Expected result:** `nginx -t` passes, reload succeeds.

### D.3 — Stop Backend A and prove continuity
**What:** Stop Backend A, send repeated requests through the domain.
**Expected result:** All requests succeed via Backend B only, no long stalls.

### D.4 — Restart and confirm recovery
**What:** Restart Backend A, repeat requests.
**Expected result:** Both backends alternate again.

### D.5 — Name the remaining single point of failure
**What:** State which component is still a SPOF.
**Answer:** Mac 2 (the edge) — only one nginx instance exists.

---

## Extension E — Controlled Edge Migration (DNS-Based Cutover)
**Owner: Priyal**

### E.1 — Stand up a standby nginx
**What:** Configure a second nginx instance with the same config on Mac 3 or Mac 4 temporarily.

### E.2 — Update the DNS record to point at the standby
**What:** Change the dnsmasq record, restart dnsmasq.

### E.3 — Observe TTL effects during the cutover
**What:** A client briefly still hits the old edge until its cache expires, then shifts automatically.
**Note:** Depends on Extension B's short TTL already being in place — run B before E.

### E.4 — Explain the no-new-hardware constraint
**What:** Explain why this needed no new physical machine.

---

## Extension F — Faculty-Injected Troubleshooting Challenge
**Owner: Everyone, live, during evaluation**

Diagnose in strict layer order, narrating out loud: DNS → TCP → TLS → Application. Partial credit for correct methodology even without a full fix.

---

## Phase 2 additions to the Final Demonstration Sequence

| # | Step | What the evaluator expects |
|---|---|---|
| 9 | Demonstrate Phase 2 resilience behavior | Backup DNS failover (A), TTL/cache behavior (B), HA failover (D), edge migration (E) — shown live |
| 10 | Diagnose the faculty-injected fault | Correct layer identified, systematic diagnosis narrated |
| 11 | Individual viva questions | Every member explains the full system end-to-end |

## Phase 2 deliverable additions

- **Configuration Bundle:** backup dnsmasq config (Vaishnavi), updated nginx config with `max_fails`/`fail_timeout` (Priyal/Anusha), standby nginx config (Priyal), firewall rules + rollback copy (Anusha)
- **Evidence Folder additions:** backup DNS resolving with primary down, TTL expiry + manual flush screenshots, firewall blocking direct backend access, HA failover sequence, DNS cutover to standby edge with TTL-window behavior
- **Phase 2 Final Report:** one paragraph per extension, written by whoever owns that extension
- **Individual viva prep:** everyone should be able to explain all five extensions and the full DNS → TCP → TLS → HTTP → load-balancing path
