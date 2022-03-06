# Docker Overview

This is a little dashboard to show what IPs your docker containers have.
Particulary useful for using a VPN within a docker network (for example with combination with pihole).

## Deployment options

- Docker (build)
- Docker (ghcr.io)
- Local

## Docker deployment:

```
docker-compose build .
docker-compose up -d
```

## Using github container registry (ghcr.io)

`docker run ghcr.io/kuhnchris/minidockerregistry:latest`

## Local deployment:

Requirements: 
- local docker install (usually accessable via `/var/run/docker.sock`)

1. (optional) create a venv `venv ./venv`
2. (optional) `source ./venv/bin/activate`
3. pip install -r requirements.txt
4. flask run

Access the app using http://localhost:5000

Want to have it accessable not just from localhost?
Replace `flask run` with `flask run --host=0.0.0.0`.

Want autoreloading for development?
Replace `flask run` with `FLASK_ENV=development flask run`

Runing auto-reload without localhost-restriction is not recommended.
