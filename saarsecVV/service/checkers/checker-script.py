from gamelib import *
from pwn import * 
import random
from data import cities

class SaarsecVVInterface(ServiceInterface):
    name = 'SaarsecVV'

    def check_integrity(self, team: Team, tick: int):
        assert(1 == 1, 'Calculation failed')
        # check it with an original implementation
        # or just check wether the tickets produced are right

        # do i haveto check connection here aswell?
        

    def store_flags(self, team: Team, tick: int):
        # store flags via group-tickets

        start_num = random.randint(0, len(cities) - 1)
        goal_num = random.randint(0, len(cities) -1)
        group_size = random.randint(15, 30)
        date = "{day:02d}.{month:02d}.2023".format(day=randint(1, 29), month=randint(1, 12))
        names = []
        for x in range(10, group_size):
            names.append(usernames.generate_name)
        goal = cities[goal_num]
        start = cities[start_num]
        groupname = "GAMEMASTERS"

        try:
            r = remote(team, 5445)
            r.rev()
            r.sendline(b'2')
            r.recv()
            r.send(str(group_size).encode())
            r.recv()
            r.send(groupname.encode())
            r.recv()
            r.send(goal.encode())
            r.recv()
            r.send(start.encode())
            r.recv()
            r.send(date.encode())

            # now loop and send all names + flags as persons in the group


            # exit cleanly     
            r.recv()
            r.sendline(b'4')
            r.close()


        except:
            r.close()
            raise OfflineException

 

    def retrieve_flags(self, team: Team, tick: int):
        r = remote(team, 5445)
        r.recv()
        r.send(b'3')
        r.recv()   
        r.send(directory_name.encode())
        r.recv()
        r.send(dir_pwd.encode())
