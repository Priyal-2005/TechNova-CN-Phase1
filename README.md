# TechNova CN Project Phase 1

## Team Members

- Priyal Sarda [2401010354] — DNS Admin (Mac 1)
- Anusha Prathapani [2401010344] — Edge Engineer (Mac 2)
- Kashika Agarwal [2401010215]— Backend Dev A (Mac 3)
- Vaishnavi Dhanai [2401010489] — Backend Dev B (Mac 4)

## Architecture

Four machines, each with one role:

- **Mac 1**: Private DNS server (dnsmasq)
- **Mac 2**: Edge — nginx reverse proxy, TLS termination, load balancing
- **Mac 3**: Backend A — REST API on port 3001
- **Mac 4**: Backend B — REST API on port 3002

Request flow: Client → DNS query (Mac 1) → HTTPS request (Mac 2) → Backend A or B (Mac 3/4)

See `docs/topology-diagram.png` and `docs/architecture-doc.md` for full details.

## How to Run the Backends

### Backend A (port 3001)

Backend A is a Python REST API running on port 3001.

#### Run Backend A

    cd ~/cn-project/backend-a
    python3 app.py

The server should display:

    Backend A listening on port 3001

#### Test Backend A

Open another Terminal window and run:

    curl -i http://localhost:3001/api/status

Expected response should contain:

    X-Backend: A
    Cache-Control: max-age=60

and:

    {"backend": "A", "status": "ok"}

Backend A listens on 0.0.0.0:3001 so that other computers on the same network can access it.

### Backend B (port 3002)

    cd backend-b
    python3 app.py

Test:

    curl http://localhost:3002/api/status

## DNS Setup (dnsmasq — Mac 1)

Config file: dnsmasq/dnsmasq.conf

To reproduce:

    brew install dnsmasq
    cp dnsmasq/dnsmasq.conf /opt/homebrew/etc/dnsmasq.conf
    sudo brew services start dnsmasq

## Edge / Load Balancer Setup (nginx — Mac 2)

Config file: nginx/nginx.conf

Certificate: certs/app.team1.test.crt (public cert only — private key is not committed)

To reproduce:

    brew install nginx
    cp nginx/nginx.conf /opt/homebrew/etc/nginx/nginx.conf
    brew services start nginx
