# installation

## reference guide
https://linuxhint.com/install_docker_raspberry_pi-2/

## update beforehand
`sudo apt-get update`
`sudo apt-get full-upgrade -y`
`sudo reboot`

## download and install docker
`cd ~/Downloads/`
`curl -fsSL https://get.docker.com -o get-docker.sh`
`sudo bash get-docker.sh`
`sudo usermod -aG docker $(whoami)`
`sudo reboot`

## verify docker is installed
`docker version`

## install docker compose
`sudo apt-get install docker-compose` 

## make new folder for home assistant
`mkdir ~/home-assistant/`

`docker run -d \
  --name homeassistant \
  --privileged \
  --restart=unless-stopped \
  -e TZ=MY_TIME_ZONE \
  -v /home/pi/home-assistant:/config/ \
  --network=host \
  ghcr.io/home-assistant/raspberrypi4-homeassistant:stable`

# using home assistant with docker

## go to home assistant
http://hostname:8123

## restart
`docker restart homeassistant`

## YAML file to make running docker easier
`cd ~/home-assistant/`
`nano docker-compose.yml`

```
version: '3'
services:
  homeassistant:
    container_name: homeassistant
    image: "ghcr.io/home-assistant/raspberrypi4-homeassistant:stable"
    volumes:
      - /home/pi/home-assistant:/config/
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    privileged: true
    network_mode: host
    devices:
- /dev/ttyAMA0:/dev/ttyAMA0
```

## run docker from YML
`docker-compose up -d`

## update home assistant
if this returns "Image is up to date" then you can stop here
`docker pull ghcr.io/home-assistant/raspberrypi4-homeassistant:stable`

stop the running container
`docker stop homeassistant`

remove it from Docker's list of containers
`docker rm homeassistant`

finally, start a new one
`docker run -d \
  --name homeassistant \
  --restart=unless-stopped \
  --privileged \
  -e TZ=MY_TIME_ZONE \
  -v /home/pi/home-assistant:/config/ \
  --network=host \
  ghcr.io/home-assistant/raspberrypi4-homeassistant:stable`
