# Docker Overview

This is a little dashboard to show what IPs your docker containers have. Particularly useful for using a VPN within a docker network (for example with combination with `pihole`).

**Update 2022**: This now also includes an integrated DNS server to use with `pihole`, as all the "common" workarounds are... stupid or hamfisted, at best. - Now you can simply add your favorite DNS prefix (currently hardcoded as `"vpn.local"`) and dig all your domains either by `dig -x *.vpn.local` (returns all services) or `dig -x container-name.vpn.local` to get the current IP of the service you want to access.

The whole reason for this is, that there are `django` apps that do not like domains which are not `RFC1034` conform. I would have used the local DNS service included in `docker` (basically: `service.docker_network_name`, for example: `nginx.vpn_network`), but these are, if you didn't explicitly name your `docker network` in such a way, conform to the RFC, so `django` is throwing hands (again).

**Update 2022 #2**: Due to needing this for myself (mostly due to developing Matrix bots) I actually took the time to refactor this project into modules and include options to enable and disable services via environment parameters. Please check the included `docker-compose.yml` for more options.

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

`docker run ghcr.io/kuhnchris/minidockerregistry:latest -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080`

## Local deployment:

### Requirements: 

- local docker install (usually accessable via `/var/run/docker.sock`)
- `pipenv` (package: `python3-pipenv` or `py3-pipenv`) installed

### Install instructions:

- `pipenv install`

### Run instructions:

- `ENABLE_HTTP=1 ENABLE_DNS=1 pipenv run python3 app/app.py`

### Notes:
- Access the app: http://localhost:8080
- Test the DNS server by using `dig` (requires package `bind-utils` of your operation system):  `dig \*.dev.local -p 8853 @localhost` 
    - Make sure to `\` the `*` to avoid shell expandation
- To enable `auto-reload` set the environment variable `ENABLE_FLASK_DEBUG` to any value that is not `"False"`.

### Supported enviromental flags:

|Module|Variable|Default Value|Explanation|
|-|-|-|-|
||||**Parameters**|
|DNS|LOCAL_DOMAIN|vpn.local|The DNS domain the DNS server responds to|
|DNS|DNS_PORT|53|DNS server port|
|HTTP|HTTP_PORT|8080|HTTP port|
|HTTP|HTTP_HOST|localhost|HTTP host to listen to |
||||**Flags**|
|DNS|ENABLE_DNS|False|Enables the DNS module & server|
|HTTP|ENABLE_HTTP|False|Enables the HTTP module & server|
|HTTP|ENABLE_FLASK_DEBUG|False|Enable `auto_reload` and `werkzeug` debug mode|