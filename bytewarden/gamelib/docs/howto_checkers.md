[(back to gamelib manual)](../README.md)

HowTo Checkerscripts
====================

A checkerscript is a python3-script that connects to your service, checks its functionality, stores flags and retrieves them again.
 
Your gameserver script should be in `/checkers/` in your service repository, filename doesn't matter. 
You have to inherit from the `ServiceInterface` class in [gamelib.py](../gamelib.py).
See [gamelib-sample.py](../gamelib-sample.py) or the [example service checker](https://github.com/MarkusBauer/saarctf-example-service/blob/master/checkers/interface.py) how to do this.

The basic template might look like this:

```python
from gamelib import *

class YourServiceInterface(ServiceInterface):
    name = '...'

    def check_integrity(self, team: Team, tick: int):
        assert(1 == 1, 'Calculation failed')
        ...

    def store_flags(self, team: Team, tick: int):
        flag = self.get_flag(team, tick)
        ...

    def retrieve_flags(self, team: Team, tick: int):
        ...
```
Every method should return (in case of success) or throw one of these gamelib exceptions to signal other states. 
The message of these exceptions will be visible for teams.
- `OfflineException` (or `requests.ConnectionError` / pwntools `Could not connect` error / `OSError no route to host`)
- `MumbleException` (or `AssertionError`)
- `FlagMissingException`

Finally you need to configure the checkerscript - edit `/checkers/config` in your service repository, 
it should contain one line formatted `your_script.py:YourClassName`.  


Guidelines
----------
- Write Python 3 (gameserver uses Python 3.7+)
- You should only throw the `gamelib` exceptions - with everything other exception we will consider your script as "crashed".
- Do I/O only with a timeout (for example: `gamelib.TIMEOUT` seconds)
- To get nice usernames, use `gamelib.usernames.generate_name()`.
- Be verbose - especially in error cases. From the stdout/stderr output you should always be able to tell what's wrong. 
  (We collect your script's output, but don't show it to teams).
- Watch your imports:
  - Use absolute imports for the gamelib
  - Use relative imports for additonal files in your project
  - `./gamelib/run-checkers` will scream if you violate these rules
  ```python
  import requests
  import gamelib
  from gamelib import ServiceInterface, usernames
  from . import my_additional_file
  from .my_additional_file import secret_method
  ```
- Try no to leak resources, always close your connections properly (using `try: finally:`). 
- Do not store anything in global variables, files etc. If you need to persist data between invocations use Redis (see below).
- *to be continued ...*


Persistent State
----------------
Your checker script might run in different processes and on different machines. 
To store any data (for example generated usernames / passwords) for late use check out `ServiceInterface.store` and `ServiceInterface.load`:
```python
def store_flags(self, team: Team, tick: int):
    username = usernames.generate_name()
    password = usernames.generate_password()
    self.store(team, tick, 'credentials', [username, password])

def retrieve_flags(self, team: Team, tick: int):
    data = self.load(team, tick, 'credentials')
    username, password = data
```


Useful methods
--------------
The ServiceInterface contains more useful methods, for example to find flags in text or parse flags.
There's also `assert_requests_response` to check the return code and type of a request. 
The `usernames` module contains useful functions to generate random usernames, passwords, names flags or strings.
Check out the source code for documentation. 


Multiple Flags
--------------
You can store multiple flags per tick. Use the third parameter of `get_flag` to give each flag a type / payload:
```python
def store_flags(self, team: Team, tick: int):
    flags = [self.get_flag(team, tick, 0), self.get_flag(team, tick, 1), self.get_flag(team, tick, 2)]
```

The flag payload does not necessarily need to match the number of flags. 
The following example gives out 2 flags per tick, but has 4 possible flag types / payloads. 
Flags of type 3 are given out each tick, flags of type 0, 1 and 2 are given out every third tick:
```python
def store_flags(self, team: Team, tick: int):
    flags = [self.get_flag(team, tick, tick % 3), self.get_flag(team, tick, 3)]
```

Please document your choice somewhere, it needs to be configured when importing your service in the gameserver.
 
 
Flag IDs
--------
Flag IDs are strings that are given to the players and can be used to identify certain flags. 
They can be used to simulate usernames etc. that will be known for attackers.
Flag IDs are completely optional and usually not needed.
 
To use flag IDs in your service first configure their types in a global variable `flag_id_types`. 
Then use `self.get_flag_id` to get identifiers of the registered type. 

```python
class YourServiceInterface(ServiceInterface):
    name = '...'
    flag_id_types = ['username', 'hex12', 'alphanum15']

    def store_flags(self, team: Team, tick: int):
        username1 = self.get_flag_id(team, tick, 0)  # a valid-looking username
        flag1 = self.get_flag(team, tick, 0)
        username2 = self.get_flag_id(team, tick, 1)  # 12 hexadecimal chars [0-9a-f]
        flag2 = self.get_flag(team, tick, 1)
        username3 = self.get_flag_id(team, tick, 2)  # 15 alphanumeric chars [0-9A-Za-z]
        flag3 = self.get_flag(team, tick, 2)
```

Please inform organisators in time if you use flag IDs, they might need to update the website description.    


Additional Dependencies
-----------------------
If you need additional software to run your checkerscript (python modules, system packages) you can install them in your service's `dependencies.sh`. 

1. Please check first if the package you need is already preinstalled. 
2. Then check if the package can be installed from Debian Bullseye's repository (using `apt`). 
   These packages are usually more stable and don't change that often.
3. If not, you can freely use `python3 -m pip install`. 

We have preinstalled (at least): 
- Python3 with pip
- redis
- requests
- pwntools
- numpy
- pycryptodome
- beautifulsoup4
- pytz

