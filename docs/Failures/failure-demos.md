# Failure Demonstrations — Team TechNova (CN Phase 1)

Infrastructure: Type 1 — 4 physical macOS laptops on the same LAN.
Mac 1 = private DNS (dnsmasq) · Mac 2 = edge/load balancer (nginx, TLS termination, round-robin) · Mac 3 = Backend A · Mac 4 = Backend B / test client.

Each test below shows the command run, the actual terminal output captured, and what it demonstrates about the system's behavior under failure.

---

## Test 1 — Client pointed at the wrong DNS server

**Setup:** Client's DNS resolver was set to a public DNS server (8.8.8.8) instead of the private dnsmasq server (Mac 1), so `app.technova.test` — a private `.test` domain that only dnsmasq knows about — cannot resolve.

**Commands run:**
```
sudo dscacheutil -flushcache
dig app.technova.test
curl -v https://app.technova.test:8443/api/status
ping 10.7.12.92
```

**Output:**
```
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 48134
;; SERVER: 8.8.8.8#53(8.8.8.8)
;; WHEN: Sat Oct 03 18:37:28 IST 2026

curl -v https://app.technova.test:8443/api/status
* Could not resolve host: app.technova.test
* Closing connection
curl: (6) Could not resolve host: app.technova.test

ping 10.7.12.92
64 bytes from 10.7.12.92: icmp_seq=0 ttl=64 time=8.112 ms
...
12 packets transmitted, 12 packets received, 0.0% packet loss
```

**What this demonstrates:** Public DNS has no record of a private `.test` domain, so it correctly returns `NXDOMAIN`, and `curl` fails at the resolution step with `Could not resolve host` before any network connection is even attempted. The `ping` to the edge server's raw IP succeeds, confirming the LAN path itself is fine — the failure is isolated entirely to DNS resolution, exactly as expected for this test.

---

## Test 2 — dnsmasq misdirection (stale/incorrect DNS record)

**Setup:** Client's DNS resolver correctly points at the private dnsmasq server (10.7.17.84), but dnsmasq's record for `app.technova.test` is pointing at an incorrect/stale IP address rather than the real edge server.

**Commands run:**
```
sudo dscacheutil -flushcache
dig app.technova.test
curl -v https://app.technova.test:8443/api/status
```

**Output:**
```
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 41524
;; ANSWER SECTION:
app.technova.test.   0   IN   A   10.7.0.238
;; SERVER: 10.7.17.84#53(10.7.17.84)
;; WHEN: Sat Oct 03 18:45:38 IST 2026

curl -v https://app.technova.test:8443/api/status
* Host app.technova.test:8443 was resolved.
* IPv4: 10.7.0.238
*   Trying 10.7.0.238:8443...
* connect to 10.7.0.238 port 8443 from 10.7.5.97 port 51241 failed: Operation timed out
* Failed to connect to app.technova.test port 8443 after 75073 ms: Couldn't connect to server
curl: (28) Failed to connect to app.technova.test port 8443 after 75073 ms: Couldn't connect to server
```

**What this demonstrates:** Unlike Test 1, DNS resolution itself succeeds this time (`NOERROR`, a valid-looking A record) — but the IP it hands back (`10.7.0.238`) is not a live, reachable host on the LAN, so the TCP connection attempt simply times out after ~75 seconds. This isolates the difference between a DNS failure (Test 1) and a DNS *misdirection* failure: the query succeeds, but the answer is wrong, so the client wastes a long timeout window trying to reach a dead address before giving up.

---

## Test 3 — Backend A stopped (single-backend failure under load balancing)

**Setup:** With dnsmasq and nginx both healthy, Backend A (Mac 3) was deliberately stopped (`Ctrl+C` on the running `python3 app.py` process) while nginx continued round-robin routing between Backend A and Backend B.

**Commands run (on Mac 2, the edge server):**
```
sudo lsof -i :8443
tail -50 /opt/homebrew/var/log/nginx/error.log
```

**Output:**
```
COMMAND   PID   USER    FD   TYPE       DEVICE            SIZE/OFF NODE NAME
nginx    16155  root    6u  IPv4  0xe964dd18b70c8067       0t0   TCP *:pcsync-https (LISTEN)
nginx    16156  nobody  6u  IPv4  0xe964dd18b70c8067       0t0   TCP *:pcsync-https (LISTEN)

2026/10/03 18:25:26 [error] 16156#0: *5 upstream timed out (60: Operation timed out) while connecting to upstream,
client: 10.7.5.97, server: app.technova.test, request: "GET /api/status HTTP/1.1",
upstream: "http://10.7.0.238:3001/api/status", host: "app.technova.test:8443"
```

**What this demonstrates:** nginx itself is confirmed up and listening (`lsof` shows both worker processes bound to 8443). Its error log shows exactly what happens when round-robin sends a request to the now-stopped Backend A: nginx waits for the full `proxy_connect_timeout` (60 seconds, the default) before logging an `upstream timed out` error — because nginx has no active health checks (`max_fails`/`fail_timeout`) configured, it doesn't proactively mark Backend A as down, so every request that happens to land on it during this window stalls for a full minute instead of failing over instantly to Backend B.

---

## Test 4 — Repeated requests while edge server IP is stale in DNS

**Setup:** A related angle on DNS staleness: the client repeatedly retried the request against the edge server's old, previously-correct IP (`10.7.12.92`) after that IP had drifted via DHCP to a new address, simulating what happens if DNS isn't updated promptly after an edge-server IP change.

**Commands run:**
```
curl -v https://app.technova.test:8443/api/status   # run 3 times in a row
```

**Output (all three attempts identical):**
```
* Host app.technova.test:8443 was resolved.
* IPv4: 10.7.12.92
*   Trying 10.7.12.92:8443...
* connect to 10.7.12.92 port 8443 from 10.7.5.97 port 51265 failed: Operation timed out
* Failed to connect to app.technova.test port 8443 after 75022 ms: Couldn't connect to server
curl: (28) Failed to connect to app.technova.test port 8443 after 75022 ms: Couldn't connect to server
```

**What this demonstrates:** Every retry against the stale IP fails identically and takes the same ~75-second timeout to fail — there's no caching or backoff behavior that makes repeated attempts faster or smarter. This shows that once DNS is stale, the failure is fully deterministic and repeatable until the DNS record is corrected (which is exactly what happened later when Mac 2's current IP was confirmed with `ipconfig getifaddr en0` and dnsmasq was updated and restarted).

---

## Test 5 — Both backends down (edge server up, no backend reachable)

**Setup:** Both Backend A and Backend B were stopped while nginx (now on its current IP, `10.7.18.237`, after DNS was corrected) remained running, to see how the edge server behaves when it has no live upstream at all.

**Commands run:**
```
curl -v https://app.technova.test:8443/api/status
```

**Output:**
```
* Host app.technova.test:8443 was resolved.
* IPv4: 10.7.18.237
*   Trying 10.7.18.237:8443...
* Connected to app.technova.test (10.7.18.237) port 8443
* (304) (OUT), TLS handshake, Client hello (1):
* (304) (IN), TLS handshake, Server hello (2):
* (304) (IN), TLS handshake, Certificate (11):
* (304) (IN), TLS handshake, CERT verify (15):
* (304) (IN), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256
* Server certificate: subject: CN=app.technova.test ... SSL certificate verify ok.
> GET /api/status HTTP/1.1
> Host: app.technova.test:8443
<
< HTTP/1.1 502 Bad Gateway
< Server: nginx/1.31.6
< Content-Type: text/html;charset=utf-8
<
<html><head><title>502 Bad Gateway</title></head>
<body><center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.31.6</center></body></html>
* Connection #0 to host app.technova.test left intact
```

**What this demonstrates:** This cleanly isolates the edge layer from the backend layer. The TCP connection succeeds, and the full TLS 1.3 handshake completes perfectly (client hello → server hello → certificate → cert verify → finished) — nginx and its certificate are entirely healthy and reachable. It's only *after* the TLS session is established and nginx tries to proxy the request to a backend that the failure appears, as a fast, clean `502 Bad Gateway` (not a timeout, since both backends are immediately refusing connections rather than hanging) — correctly reported by nginx itself as the proxy layer.

---

## Test 6 — Hitting a closed port directly

**Setup:** A direct connection attempt was made to a port (9999) on the edge server that nothing is listening on, to show the baseline "service not running here at all" failure mode, as distinct from a timeout or a 502.

**Commands run:**
```
curl -v http://10.7.18.237:9999
```

**Output:**
```
*   Trying 10.7.18.237:9999...
* connect to 10.7.18.237 port 9999 from 10.7.5.97 port 51291 failed: Connection refused
* Failed to connect to 10.7.18.237 port 9999 after 1013 ms: Couldn't connect to server
curl: (7) Failed to connect to 10.7.18.237 port 9999 after 1013 ms: Couldn't connect to server
```

**What this demonstrates:** Because nothing is bound to port 9999 on that host, the OS immediately sends back a TCP `RST` (connection refused) rather than letting the connection hang — the failure is reported in about 1 second, dramatically faster than the ~60–75 second timeouts seen in Tests 2–4. This is the clearest contrast in the whole set: a closed port fails fast and explicitly, while a routable-but-dead IP (stale DNS, stopped backend with no health checks) fails slow and silently, which is exactly the distinction this test set is meant to illustrate.

---

## Summary table

| # | Failure injected | Symptom | Time to fail | Layer isolated |
|---|---|---|---|---|
| 1 | Client DNS set to public resolver (8.8.8.8) | `NXDOMAIN` → `curl: (6) Could not resolve host` | Instant | DNS resolution |
| 2 | dnsmasq record points to wrong/dead IP | DNS succeeds, TCP connect times out | ~75s | DNS data correctness |
| 3 | Backend A stopped, no nginx health checks | nginx logs `upstream timed out (60s)` | 60s (per request routed to A) | Load balancer → backend |
| 4 | Edge server IP stale in DNS (post-DHCP-drift) | Deterministic, repeatable connect timeout | ~75s each | DNS freshness |
| 5 | Both backends stopped | TLS succeeds, nginx returns `502 Bad Gateway` | Fast (seconds) | Backend availability |
| 6 | Closed port (nothing listening) | `Connection refused` (TCP RST) | ~1s | Port/service availability |

Evidence source: terminal screenshots captured during live testing on Team TechNova's 4-Mac LAN setup (Oct 3, 2026).
