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
`http://hostname:8123`

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

## run docker from YML (must be in home assistant dir)
`docker-compose up -d`

## update home assistant
if this returns "Image is up to date" then you can stop here
`docker pull ghcr.io/home-assistant/raspberrypi4-homeassistant:stable`

stop the running container
`docker stop homeassistant`

remove it from Docker's list of containers
`docker rm homeassistant`

finally, start a new one
`docker-compose up -d`

# installing pyscript

## reference
https://github.com/custom-components/pyscript
https://hacs-pyscript.readthedocs.io/en/stable/overview.html

## obtain master branch of pyscript and install to home assistant dir
```
cd ~/Downloads
git clone https://github.com/custom-components/pyscript.git
mkdir -p ~/home-assistant/custom_components
cp -pr ~/Downloads/pyscript/custom_components/pyscript ~/home-assistant/custom_components
rm -rf ~/Downloads/pyscript
```

## add integration to home assistant config
`cd ~/home-assistant`
`nano configuration.yaml`

add the following lines:
```
# pyscript setup
pyscript:
  allow_all_imports: true
  hass_is_global: true
```

## to add scripts
put .py files into the `~/home-assistant/pyscript` folder and restart home assistant with `docker restart homeassistant`

## to update scripts
whenever a script file is changed call the reload pyscript service from:
 'Developer Tools' -> 'Services' -> 'Pyscript Python scripting: Reload pyscript'

# setting up Jupyter kernel for interactive development with Home Assistant

## reference
https://github.com/craigbarratt/hass-pyscript-jupyter/blob/master/README.md

## install jupyter kernel on client machine (i.e. your PC) in python environment
`pip install hass_pyscript_kernel`
`jupyter pyscript install`

edit config settings in this file:
`C:\ProgramData\jupyter\kernels\pyscript/pyscript.conf`

* hass_host: the host name or IP address where your HASS instance is running
* hass_url: with the URL of your HASS httpd service
* hass_token: with a long-lived access token created via the button at the bottom of your user profile page in HASS.
* hass_proxy: with proxy url to use if HASS is not directly reachable. e.g. when using SSH to access your HASS instance, you can open a SOCKS5 tunnel to keep your Jupyter local.

## confirm pyscrip kernal and updated config settings
`jupyter kernelspec list`
`jupyter pyscript info`

## start Jupyter notebook
`jupyter notebook .\pyscript_tutorial.ipynb`

## to make sure logging info is visible run this at the beginning cell of a notebook
```
import logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
```