[HowTo build/install](docs/howto_build_install.md) | [HowTo checker scripts](docs/howto_checkers.md) | [HowTo exploits](docs/howto_exploits.md)

saarCTF Service Structure
=========================

This repository contains everything you need to build a service for saarCTF. You'll find utils to build, install and test your service.

Basics
------
Every service should be a repository in our Gitlab that follows the structure 
of this [example service](https://github.com/MarkusBauer/saarctf-example-service).

Create a new service
--------------------
To create a new service you need to:
1. Fork the [example service](https://github.com/MarkusBauer/saarctf-example-service) to your Gitlab account
2. Rename your fork to an actual name (possibly wip): Go to "Settings" => "General" and set a name, 
   then open the "Advanced" tab and "Change path". 
3. Clone your repository, then run `git submodule update --init`
4. Code it!


Overview
--------
This is the service pipeline summarized:
```
                                                                 /  =>  (install.sh in docker)     =>  local test container
[service repo]  =>  (build - build.sh)  =>  [service artifacts]  |- =>  (install.sh in CI docker)  =>  Gitlab CI unit tests
       |                                                         \  =>  (install.sh in vulnbuild)  =>  vulnbox
       |                                                                                                   ^
       |                                                                                                   |
       |-  =>  (/checkers + dependencies.sh)  =>  [checker scripts]    ---------->  run against  ----------/
       \_  =>  (/exploits + dependencies.sh)  =>  [sample exploits]    ------> can be tested against -----/
```

The service is first **built** in a docker container. 
The build artifacts are used to **install** the service - either in a docker container or on an actual Virtualbox-based VM.
In parallel, the service **checker** script will be loaded by the gameserver infrastructure and will run against the installed service (either VM or Docker). 
Finally the sample **exploits** will be used to test that the vulnerabilities are actually exploitable. 
All steps can be tested with the provided Gitlab CI configuration. 

If in doubt, all operating systems will be Debian Bullseye and have at least Python3 installed.


Functions
---------
You can invoke gamelib's testing functionality either by using the CI or by calling these scripts by hand (in your service repo root):
- `gamelib/run-build` - build the service (test `build.sh`) and store output in `./build_output`
- `gamelib/run-install` - create a docker image containing your service (test `install.sh`)
- `docker-compose up [-d]` - start a container with your service image to test against
  - use `-d` to start in detached mode
  - the container writes his IPs to `./docker-container-infos.txt` once started
- `gamelib/run-checkers` - run unit tests against your checker script to find basic errors. Service docker container must be running.
- `gamelib/run-exploits` - test your exploits against your service docker container.


Manual
------
- [Howto Service Build and Installation](docs/howto_build_install.md)
- [Howto write checker scripts](docs/howto_checkers.md)
- [Howto write exploits](docs/howto_exploits.md)

