# Extension C — Service Isolation (Backend Firewall Rules)

Restricts direct access to the backend ports so only Mac 2 (Anusha, the edge/nginx
host) can reach them — all other LAN clients must go through nginx.

- `extension-c-backendA.pf` — applied on Mac 3 (Kashika), restricts port 3001
- `extension-c-backendB.pf` — applied on Mac 4 (Vaishnavi), restricts port 3002

Both rules allow only `10.7.30.136` (Mac 2's IP at time of testing) and drop all
other inbound TCP connections to that port.

Applied via:
```
sudo pfctl -a com.apple/extension-c -f /etc/pf.anchors/extension-c
sudo pfctl -E
```

**Rollback:** the original `/etc/pf.conf` was backed up to
`/etc/pf.conf.extension-c-backup` on both machines before any change, and
verified identical via `cmp` before applying the rule. The restriction was
removed with `sudo pfctl -d` on both machines once evidence was captured,
and a cross-machine retest confirmed both ports were reachable again.

See `phase-2/docs/evidence/extension-c-*` for the before/after/rollback
screenshots.
