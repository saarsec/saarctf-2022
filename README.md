# saarCTF 2022

Services from [saarCTF 2022](https://ctftime.org/event/1611).

## Building services
Enter a service directory and use `docker-compose`, e.g.:
```bash
cd bytewarden
docker-compose up --build -d
```

## Running checkers
Every service comes with a `checkers` directory, which contains a python-script named after the service.
Running this script should place three flags in the service and try to retrieve them subsequently.
Caveat: Make sure the `gamelib` is in the `PYTHONPATH`, e.g.:
```bash
PYTHONPATH=.. python3 bytewarden.py [<ip>]
```

Checkers require a Redis instance to store information between ticks. 
If you don't have redis installed locally, use the environment variables `REDIS_HOST` and `REDIS_DB` to configure one.


## Flag IDs and exploits
The script `get_flag_ids.py` prints you the flag ids used to store the demo flags.

Each service comes with demo exploits to show the vulnerability.
To run an exploit: `python3 exploit_file.py <ip> [<flag-id-of-type1> <flag-id-of-type-2> ...]`


## Special Cases
### backd00r
This services communicates over ICMP ping packets, which makes its deployment harder:
By default, it is attached to the host's network adapter. You can reach it as `localhost`, but it is *reachable from your local network*.
To change that, uncomment `network_mode: host` in `docker-compose.yml`. Then you have to find out the container's IP to connect to it.

This service is slightly different from the real one played in the CTF, to comply with an in-docker setup:
1. The isolation of mining scripts is weaker, because docker does not allow nested namespaces
2. The kernel module is disabled. Checkers and demo exploits can still talk to the service.

Finally, ICMP is only available by raw sockets, meaning you must be `root` to run checkers or exploits. Use `sudo`.


### SaarCloud
Use `127.1.0.1` instead of `127.0.0.1`. 
We use urls of the form `username.127.1.0.1.nip.io` to get hostnames to the service. 
Some consumer routers block `127.0.0.1` (dns rebinding protection), but not other localhost IPs.
