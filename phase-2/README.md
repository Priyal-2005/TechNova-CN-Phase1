# Phase 2 — Harden, Recover & Troubleshoot

Extends the Phase 1 network with resilience and recovery behavior across the
same 4 Macs — nothing was rebuilt from scratch.

| Extension | Owner | What it covers |
|---|---|---|
| A — Backup DNS Resolver | Vaishnavi | second dnsmasq instance, DNS failover |
| B — DNS TTL & Controlled Record Change | Kashika | TTL caching, auto-expiry, manual flush |
| C — Service Isolation (Firewall Rules) | Anusha | pf rules restricting backend ports to the edge only |
| D — High-Availability Failover | Priyal | nginx `max_fails`/`fail_timeout`, backend stop/restart continuity |
| E — Controlled Edge Migration | Priyal | standby nginx + DNS-based cutover |
| F — Faculty-Injected Troubleshooting | Everyone | live, during evaluation |

- `dnsmasq-backup/` — Vaishnavi's backup DNS config (Extension A)
- `nginx-standby/` — standby edge config used for the Extension E cutover
- `firewall/` — pf rules + rollback notes (Extension C)
- `docs/phase-2-task-guide.md` — full step-by-step guide (what/why/expected result per extension)
- `docs/evidence/` — all Phase 2 screenshots, organized by extension

See the root `README.md` for the full team/role table and overall repo layout,
and the task guide above for detailed steps and reasoning per extension.
