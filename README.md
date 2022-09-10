# Docker Overview

This is a little dashboard to show what IPs your docker containers have.
Particularly useful for using a VPN within a docker network (for example with combination with pihole).

Update 2022: This now also includes an integrated DNS server to use with `pihole`, as all the "common" workarounds are... stupid.
Now you can simply add your favorite DNS prefix (currently hardcoded as "vpn.local") and
dig all your domains either by `dig -x *.vpn.local` (returns all services) or `dig -x container-name.vpn.local` to get the current IP of the service you want to access.

The whole reason for this is, that there are django apps that do not like domains which are not RFC conform. I would have used the local DNS
of docker (basically: `service.docker_network_name`, for example: `nginx.vpn_network`), but, again, not RFC conform, so `django` is throwing hands.


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

`docker run ghcr.io/kuhnchris/minidockerregistry:latest -v /var/run/docker.sock:/var/run/docker.sock -p 8080:5000`

## Local deployment:

Requirements: 
- local docker install (usually accessable via `/var/run/docker.sock`)

1. (optional) create a venv `venv ./venv`
2. (optional) `source ./venv/bin/activate`
3. pip install -r requirements.txt
4. flask run

Access the app using http://localhost:5000

- `Q`: Want to have it accessible not just from `localhost`?
- `A`: Replace `flask run` with `flask run --host=0.0.0.0`.


- `Q`: Want auto-reloading for development?
- `A`: Replace `flask run` with `FLASK_ENV=development flask run`

Running `auto-reload` without `localhost-restriction` is not recommended.
