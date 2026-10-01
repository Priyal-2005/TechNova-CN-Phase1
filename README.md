# TechNova-CN-Phase1

## How to Run the Backends

### Backend A

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
