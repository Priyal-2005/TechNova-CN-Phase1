# Phase 2 Final Report — Team TechNova

## Overview

Phase 1 built a working private network service: a custom DNS domain (`app.technova.test`), an nginx edge handling TLS termination and load balancing, and two backend servers. Phase 1 proved the system worked under normal conditions.

Phase 2 extended the system to address resilience and operational concerns that Phase 1 testing had exposed: single points of failure, missing health-checking, open backend ports, and the need to demonstrate controlled recovery and migration procedures. Each extension below was owned by one team member and independently tested, with terminal output and screenshots captured as evidence (`phase-2/docs/evidence/`).

---

## Extension A — Backup DNS Resolver
**Owner: Vaishnavi (Mac 4)**

Phase 1 had a single DNS server (Mac 1). If it went down, the entire system became unreachable by name even though the edge and both backends were healthy — a single point of failure.

Vaishnavi configured a second dnsmasq instance as a backup resolver (`phase-2/dnsmasq-backup/dnsmasq.conf`), mirroring the same DNS records so clients could fail over to it if the primary DNS server became unavailable. Verified by taking the primary DNS down, confirming client resolution via the backup resolver, and restoring the primary afterward.

## Extension B — DNS TTL and Caching Behavior
**Owner: Kashika (Mac 3)**

Demonstrated how DNS caching and TTL (time-to-live) govern when clients see an updated DNS record. Set `local-ttl=60` on the primary dnsmasq config, then showed a record change not taking effect for existing clients until the TTL window expired, and showed a manual cache flush forcing immediate propagation. This caching/TTL mechanism is the same one Extension E relies on for its DNS-based edge migration.

## Extension C — Firewall / Service Isolation
**Owner: Anusha (Mac 2)**

Phase 1 left both backend servers' ports open to any machine on the network. Anusha used macOS's `pf` (packet filter) firewall to restrict each backend port so that only the edge server (nginx, Mac 2) could reach them directly — blocking requests from any other machine on the network (`phase-2/firewall/`). Verified by confirming a direct request from a non-permitted machine was blocked while the edge's own requests succeeded, then rolled the rule back and confirmed open access was restored.

## Extension D — High-Availability Failover
**Owner: Priyal (Mac 1)**

Phase 1's nginx had no health-checking configured, so a dead backend caused every request to stall for up to 60 seconds before failing. Added `max_fails=2 fail_timeout=10s` to nginx's `upstream backend_pool` block so unhealthy backends are detected and temporarily routed around automatically. Verified by stopping Backend A entirely and confirming all requests succeeded instantly via Backend B with zero stalls, then restarting Backend A and confirming it automatically rejoined the load-balancing rotation.

## Extension E — Controlled Edge Migration
**Owner: Priyal (Mac 1)**

Demonstrated migrating the edge server itself to a different machine with no new hardware — the same kind of zero-downtime migration a production load balancer undergoes. Stood up a second, identical nginx instance (same config and TLS certificate) on a teammate's machine as a standby edge, then changed the DNS record for `app.technova.test` to point at it and reloaded DNS. Verified via `dig` showing the domain resolving to the new standby edge, and a client request succeeding against it with no code changes anywhere else in the system.

## Extension F — Faculty-Injected Troubleshooting Challenge
**All members (readiness, no separate build)**

A live challenge where a fault is introduced into the running system and the team must diagnose and fix it under time pressure. The team prepared a structured four-layer diagnostic method — DNS → TCP → TLS → Application — with the exact command for each layer documented in the team's Notion task guide, including a check for macOS's Application Firewall, which was found during Phase 2 testing to silently block TLS connections to the unsigned nginx binary (a real bug discovered and root-caused during this project, not a hypothetical).

---

## Summary Table

| Extension | Owner | Problem Addressed |
|---|---|---|
| A — Backup DNS | Vaishnavi | Single point of failure if primary DNS goes down |
| B — DNS TTL/Caching | Kashika | Demonstrates DNS cache propagation and control |
| C — Firewall/Isolation | Anusha | Backend ports open to any machine on the network |
| D — HA Failover | Priyal | 60-second stalls when a backend fails, no health-checking |
| E — Edge Migration | Priyal | Demonstrates zero-downtime migration of the edge itself |
| F — Troubleshooting Readiness | All | Live fault diagnosis under faculty-injected failure |

## Conclusion

Phase 1 proved the system works under normal conditions. Phase 2 proved it can detect failure, survive it, recover automatically, operate under access restrictions, and be migrated live — closing the gap between a working demo and infrastructure that could be trusted in production.
