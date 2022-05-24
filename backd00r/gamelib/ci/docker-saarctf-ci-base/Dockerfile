FROM debian:bullseye

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y --no-install-recommends wget ca-certificates sudo nano htop iproute2 && \
	apt-get install -y python3 python3-pip python3-setuptools python3-wheel python3-virtualenv && \
	apt-get clean && \
	true
