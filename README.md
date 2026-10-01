# TechNova-CN-Phase1

## Backend B

Backend B is a Python HTTP server running on port 3002.

- Host: 0.0.0.0
- Port: 3002
- Endpoint: `/`
- Status endpoint: `/api/status`
- Backend identifier: `B`
- Cache-Control: `max-age=60`

### Run Backend B

```bash
python3 backend-b/app.py

curl http://localhost:3002/
curl -i http://localhost:3002/api/status
