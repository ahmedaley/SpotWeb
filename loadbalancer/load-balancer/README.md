[REST-API](/load-balancer/rest-api/README.md)

# Docker
## Storage volume
Set up docker volume: \
`docker volume create lb-volume`


In docker-compose, include (ground-level):
```
volumes:
  lb-volume:
    external: true
```
This will make it possible to connect through labels. As follows:
```
version: '3'
services:
  test:
    container_name: test
    volumes:
      - lb-volume:/var/log:rw
volumes:
  lb-volume:
    external: true

```
## Timezone
Since it can differ in timezone, every container needs to be set to the same timezone, in docker-compose.yaml set:
services:
```
  test:
    container_name: test
    environment:
      TZ: "America/New_York"
```


# Useful commands
`docker exec -it loadbalancer-rest-api /bin/bash` Connect to terminal shell in the command. 

`docker logs lb-rest-api-docker` See logs

`docker volume create lb-volume` 

`docker volume ls`

`docker volume inspect lb-volume`