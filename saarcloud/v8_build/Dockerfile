FROM ubuntu:focal

RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive \
	apt-get install -y build-essential gcc g++ nano htop git bash-completion python python3 wget curl pkg-config && \
	apt-get clean

RUN useradd -m markus
USER markus

CMD ["/code/build.sh"]