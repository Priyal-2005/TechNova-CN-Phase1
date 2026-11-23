# Phase 1 — Private Network Service Platform

Private DNS + nginx edge/load-balancer + two backend servers across 4 Macs.

- `dnsmasq/` — private DNS config (Mac 1, Priyal) for `app.technova.test` / `api.technova.test`
- `nginx/` — edge/TLS termination + load balancing config (Mac 2, Anusha)
- `backend-a/`, `backend-b/` — the two backend services (Mac 3 Kashika, Mac 4 Vaishnavi)
- `certs/` — TLS certificate and key used by nginx
- `docs/` — architecture notes, CLI command output logs, failure demos
  (`Failures/failure-demos.md`), topology diagram, and Wireshark evidence

See the root `README.md` for the full team/role table and overall repo layout.
