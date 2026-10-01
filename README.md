# TechNova CN Project Phase 1
	
## Team Members
- [2401010354] [Priyal Sarda] — DNS Admin (Mac 1)
- [2401010344] [Anusha Prathapani] — Edge Engineer (Mac 2)
- [2401010215] [Kashika Agarwal] — Backend Dev A (Mac 3)
- [2401010489] [Vaishnavi Dhanai] — Backend Dev B (Mac 4)


## Architecture
Four machines, each with one role:
- **Mac 1**: Private DNS server (dnsmasq)
- **Mac 2**: Edge — nginx reverse proxy, TLS termination, load balancing
- **Mac 3**: Backend A — REST API on port 3001
- **Mac 4**: Backend B — REST API on port 3002

Request flow: Client → DNS query (Mac 1) → HTTPS request (Mac 2) → Backend A or B (Mac 3/4)

See `docs/topology-diagram.png` and `docs/architecture-doc.md` for full details.

## How to Run the Backends
(Backend Dev A / B: fill in your section below)

### Backend A (port 3001)
```
cd backend-a
python3 app.py
Test: `curl http://localhost:3001/api/status`
```

### Backend B (port 3002)
```
cd backend-b
python3 app.py
Test: `curl http://localhost:3002/api/status`
```

## DNS Setup (dnsmasq — Mac 1)
Config file: `dnsmasq/dnsmasq.conf`

To reproduce:
```
brew install dnsmasq
cp dnsmasq/dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf
sudo brew services start dnsmasq
```

## Edge / Load Balancer Setup (nginx — Mac 2)
(Edge Engineer: fill in your section below)

Config file: `nginx/nginx.conf`
Certificate: `certs/app.team1.test.crt` (public cert only — private key is not committed)

To reproduce:
```
brew install nginx
cp nginx/nginx.conf /opt/homebrew/etc/nginx/nginx.conf
brew services start nginx
```
