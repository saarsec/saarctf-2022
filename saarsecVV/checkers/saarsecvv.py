from gamelib import *
import re
import gamelib
from pwn import remote, context
import time
import random
import sys

# context.log_level = 'debug'


TRAIN_STATION_LIST = [
'Auersmacher',
'Bachem',
'Baltersweiler',
'Beckingen',
'Besch',
'Besseringen',
'Bexbach',
'Bierbach',
'Bildstock',
'Blieskastel-Lautzkirchen',
'Bous',
'Brebach',
'Brotdorf',
'Bubach',
'Bübingen',
'Dellborner Mühle',
'Dillingen',
'Saarbrücken–Trier',
'Dirmingen',
'Dörrenbach',
'Dudweiler',
'Einöd',
'Ensdorf',
'Eppelborn',
'Fischbach-Camphausen',
'Fremersdorf',
'Friedrichsthal',
'Friedrichsthal Mitte',
'Fürth-Ostertal',
'Gennweiler',
'Gonnesweiler/Bostalsee',
'Güdingen',
'Hanweiler-Bad Rilchingen',
'Hassel',
'Haupersweiler',
'Hemmersdorf',
'Hofeld',
'Homburg Hbf',
'Illingen',
'Jägersfreude',
'Kirkel',
'Kleinblittersdorf',
'Landsweiler-Reden',
'Lebach',
'Lebach–Völklingen  ',
'Lebach-Jabach',
'Limbach (b Homburg/Saar)',
'Losheim',
'Luisenthal',
'Marth',
'Merchweiler',
'Merzig',
'Merzig Ost',
'Merzig Stadtmitte',
'Mettlach',
'Namborn',
'Nennig',
'Neunkirchen Hbf',
'Homburg–Neunkirchen',
'Nonnweiler–Neunkirchen     ',
'Neunkirchen-Wellesweiler',
'Niedaltdorf',
'Niederkirchen (Ostertal)',
'Niederlinxweiler',
'Niederlosheim',
'Nohfelden',
'Nonnweiler',
'Oberkirchen Süd',
'Oberlinxweiler',
'Osterbrücken',
'Ottweiler',
'Ottweiler–Schwarzerden',
'Ottweiler-Wingertsweiher',
'Perl',
'Quierschied',
'Rentrisch',
'Rohrbach',
'Pirmasens–Rohrbach',
'Saarbrücken-Burbach',
'Saarbrücken-Burbach-Mitte',
'Saarbrücken Hbf',
'Mannheim–Saarbrücken',
'Saarbrücken–Metz',
'Saarbrücken–Wemmetsweiler',
'Saarbrücken–Sarreguemines',
'Saarbrücken–Trier',
'Saarbrücken Messebf',
'Saarbrücken Ost',
'Saarbrücken–Sarreguemines',
'Saarhölzbach',
'Saarlouis Hbf',
'Schafbrücke',
'Scheidt',
'Schiffweiler',
'Schwarzenbach',
'Schwarzerden',
'Siersburg',
'St. Ingbert',
'St. Wendel',
'Sulzbach',
'Sulzbach Altenwald',
'Türkismühle',
'Trier–Türkismühle',
'Türkismühle–Kusel  ',
'Völklingen',
'Walhausen',
'Wemmetsweiler Rathaus',
'Werschweiler',
'Wiebelskirchen',
'Würzbach',
'Wustweiler',
]


def get_random_station() -> str:
    # service has problems with spaces (and potentially utf-8?)
    station = random.choice(TRAIN_STATION_LIST)
    station = station.strip().replace('ü', 'ue').replace('ä', 'ae').replace('ö', 'oe').replace(' ', '-')
    return station



# See the "SampleServiceInterface" from gamelib for a bigger example
# See https://gitlab.saarsec.rocks/saarctf/gamelib/-/blob/master/docs/howto_checkers.md for documentation.

class SaarsecVV(ServiceInterface):
    name = 'saarsecVV'
    flag_id_types = ["username"]

    # secretkey = ""
    # credentials = "", ""

    def check_integrity(self, team: Team, tick: int):
        # pwntools "Could not connect" exception is accepted as OFFLINE
        conn = remote(team.ip, 5445, timeout=TIMEOUT)
        try:
            data = conn.recvuntil(b'2 - No \n\n')
            assert "Welcome to the fastest way of public transportation !!" in data.decode(), 'Please do not re-code this service!'

        finally:
            conn.close()

    def store_flags(self, team: Team, tick: int):
        username = self.get_flag_id(team, tick, 0)
        flag = self.get_flag(team, tick)
        print("[ ] Flag will try to get stored: " + flag)
        # timeout to small
        conn = remote(team.ip, 5445, timeout=TIMEOUT)
        try:
            # print(b'1: ' + conn.recvuntil(b'No \n\n'))
            conn.recvuntil(b'2 - No \n\n')

            credentials = self.load(team, tick, "credentials")
            #print(credentials)
            if credentials != None:
                print("[ ] There is an existing user, login")
                conn.sendline(b'1')
                # login with already registered user
                # print(b'2: ' + conn.recvuntil(b'Please provide your username:\n'))
                conn.recvuntil(b'Please provide your username:\n')
                gm_name = credentials[0]
                gm_pw = credentials[1]
                conn.send(gm_name.encode())
                # print(b'3: ' + conn.recvuntil(b'Please provide your password:\n'))
                conn.recvuntil(b'Please provide your password:\n')
                conn.send(gm_pw.encode())
                # print(b'4: ' + conn.recvuntil(b'5 - Exit \n\n'))
                conn.recvuntil(b'5 - Exit \n\n')

            else:
                print("[ ] New user will be registered")
                # create new user
                conn.sendline(b'2')
                # print(b'2: ' + conn.recvuntil(b'Please provide a username: (20 chars max)\n'))
                conn.recvuntil(b'Please provide a username: (20 chars max)\n')
                gm_name = username
                gm_pw = gamelib.usernames.generate_password()
                # self.credentials = gm_name, gm_pw
                self.store(team, tick, "credentials", [gm_name, gm_pw])
                conn.send(gm_name.encode())

                # print(b'3: ' + conn.recvuntil(b'Provide a password: (20 chars max)\n'))
                conn.recvuntil(b'Provide a password: (20 chars max)\n')
                conn.send(gm_pw.encode())

                # print(b'4: ' + conn.recvuntil(b'5 - Exit \n\n'))
                conn.recvuntil(b'5 - Exit \n\n')

            tmp = random.randint(0,1)
            #tmp = 0
            self.store(team, tick, "id", tmp)
            # 0 -> single ticket
            if tmp == 0:
                print(" [ ] Flag will be stored in Single Ticket")
                #print(gm_name)
                conn.sendline(b'1')
                data = conn.recvuntil(b'<dd.mm.yyyy>\n')
                # TODO: get the secret key
                # print(b'5: ' + data)
                secretkey = re.search("\n(\\w{19})", data.decode())[1]
                # self.secretkey = secretkey
                self.store(team, tick, "secretkey", secretkey)
                #print(secretkey)
                #print(data)

                day = random.randint(1, 29)
                month = random.randint(1, 12)
                year = random.randint(2023, 2025)
                date = str(day) + "." + str(month) + "." + str(year)
                conn.send(date.encode())

                # print(b'6: ' + conn.recvuntil(b'Where do you want to go?\n'))
                conn.recvuntil(b'Where do you want to go?\n')
                rnd_target_city = get_random_station()
                conn.send(rnd_target_city.encode())

                # print(b'7: ' + conn.recvuntil(b'Where do you want to start?\n'))
                conn.recvuntil(b'Where do you want to start?\n')
                rnd_source_city = get_random_station()
                conn.send(rnd_source_city.encode())

                # print(b'8: ' + conn.recvuntil(b'Whos ticket is it?\n'))
                conn.recvuntil(b'Whose ticket is it?\n')
                conn.send(flag.encode())

                #time.sleep(1)
                data = conn.recvuntil(b'5 - Exit \n\n')
                #print(b'9: ' + data)
                assert re.search("\n(\\w{6,10})\n", data.decode()) != None, "Service integrity broken"
                ticketid = re.search("\n(\\d{6,10})\n", data.decode())[1]
                # check if ticket id is computed correctly
                ticket = ticketid + ":" + date + ":" + rnd_source_city + ":" + rnd_target_city + ":" + flag
                print(" [ ] Searching for ticket: " + ticket)
                assert ticket in data.decode(), "Ticket was not stored correctly"
                print(" [ ] Found matching one: " + ticket)
                self.store(team, tick, "ticketinformation", [ticketid, ticket])

                conn.sendline(b'5')
                conn.recvall()
                return


            # 1 -> group ticket
            elif tmp == 1:
                print("[ ] Flag will be stored in Group Ticket")
                #print(gm_name)
                conn.sendline(b'2')
                data = conn.recvuntil(b'How many members has your group?\n')
                secretkey = re.search("\n(\\w{19})", data.decode())[1]
                # self.secretkey = secretkey
                self.store(team, tick, "secretkey", secretkey)
                #print(secretkey)
                #print(data)

                size = random.randint(13, 25)
                print("[ ] Group ticketsize: " + str(size))
                conn.sendline(str(size).encode())

                conn.recvuntil(b'What is your group name?\n')
                conn.send(flag.encode())

                conn.recvuntil(b'Please provide the travelling date: <dd.mm.yyyy>\n')
                day = random.randint(1, 29)
                month = random.randint(1, 12)
                year = random.randint(2023, 2025)
                date = str(day) + "." + str(month) + "." + str(year)
                conn.send(date.encode())

                conn.recvuntil(b'Where do you want to travel?\n')
                rnd_target_city = get_random_station()
                conn.send(rnd_target_city.encode())

                conn.recvuntil(b'Where do you want to start?\n')
                rnd_source_city = get_random_station()
                conn.send(rnd_source_city.encode())

                # now the names
                conn.recvuntil(b'Now provide all names of the group one by one\n')
                names = []
                for i in range(0, size):
                    conn.recvuntil(b'group member')
                    name = gamelib.usernames.generate_name(1).encode()
                    names.append(name)
                    conn.send(name)

                    #time.sleep(0.1)


                data = conn.recvuntil(b'5 - Exit \n\n')
                #print(data)
                #assert re.match("(\w{10})$", data) != None, "Service integrity broken"
                ticketid = re.search("\n(\\d{6,10})\n", data.decode())[1]
                # check if ticket id is computed correctly
                userid = random.randint(0, size)
                needle = re.escape(ticketid + ":" + flag + ":" + date + ":" + rnd_source_city + ":" + rnd_target_city + ":") + "(\\w{3}:\\w*)"
                print(" [ ] Searching for ticket regexp: " + needle)
                assert re.search(needle, data.decode()) != None, "Ticket was not stored correctly"
                match = re.search(needle, data.decode())[1]
                ticket = ticketid + ":" + flag + ":" + date + ":" + rnd_source_city + ":" + rnd_target_city + ":" + match
                assert ticket in data.decode(), "Ticket was not stored correctly"
                print(" [ ] Found matching one: " + ticket)
                self.store(team, tick, "ticketinformation", [ticketid, ticket])

                conn.sendline(b'5')
                conn.recvall()
                return 1


        finally:
            conn.close()

    def retrieve_flags(self, team: Team, tick: int):
        #time.sleep(2)
        flag = self.get_flag(team, tick)
        conn = remote(team.ip, 5445, timeout=TIMEOUT)
        try:
            print("[ ] Try to obtain flag " + flag)
            conn.recvuntil(b'No \n\n')
            credentials = self.load(team, tick, "credentials")
            if credentials == None:
                raise FlagMissingException("There is no account for this tick")
            # credentials = self.credentials
            # print(credentials)
            gm_name = credentials[0]
            gm_pw = credentials[1]
            conn.sendline(b'1')

            conn.recvuntil(b'Please provide your username:\n')
            conn.send(gm_name.encode())
           
            conn.recvuntil(b'Please provide your password:\n')
            conn.send(gm_pw.encode())

            conn.recvuntil(b'5 - Exit \n\n')
            conn.sendline(b'3')

            conn.recvuntil(b'To read old bookings please provide the secret key\n')
            secretkey = self.load(team, tick, "secretkey")
            # secretkey = self.secretkey
            #print(credentials)
            #print(secretkey)
            conn.send(secretkey.encode())

            data = conn.recvuntil(b'Exit \n\n')
            #print(data)
            if flag not in data.decode():
                raise FlagMissingException("Flag not found")
            print("[ ] Flag was retrieved successfully")

            ticketid, org_ticket = self.load(team, tick, "ticketinformation")
            print("[ ] Check if right ticket gets validated successfully")
            print(" [ ] Trying right ticket: " + org_ticket)
            # check if correct flag is validated correctly
            conn.sendline(b'4')
            conn.recvuntil(b'What ticket you want to validate? \n')

            tmp = self.load(team, tick, "id")
            if tmp == 0:
                conn.sendline(b'1')
            elif tmp == 1:
                conn.sendline(b'2')

            conn.recvuntil(b'Please provide your ticket now.\n')
            conn.sendline(org_ticket.encode())

            validityCheck = conn.recvuntil(b'Exit \n\n')
            assert b'validated' in validityCheck, "Correct Ticket could not get validated!"
            print(" [ ] Right ticket was successfully validated")

            print("[ ] Check if wrong ticket validation fails")

            # flip a number and check if validation fails
            equal = True
            while equal:
                num = random.randint(0, 4)
                tmp = list(org_ticket)
                tmp[num] = str(random.randint(0, 9))
                ticket = "".join(tmp)
                if ticket != org_ticket:
                    break

            print(" [ ] Trying wrong flag: " + ticket)
            conn.sendline(b'4')
            conn.recvuntil(b'What ticket you want to validate? \n')
            # 1 => single ticket validation ,2 => group ticket validation
            conn.sendline(b'1')
            conn.recvuntil(b'Please provide your ticket now.\n')
            conn.sendline(ticket.encode())
            validityCheck = conn.recvuntil(b'Exit \n\n')
            assert b'not valid' in validityCheck, "Wrong Ticket was validated!"
            print(" [ ] Wrong ticket validation failed successfully")

            # leave service
            conn.sendline(b'5')
            return 1



        finally:
            conn.close()


if __name__ == '__main__':
    # USAGE: python3 interface.py                      # test against localhost
    # USAGE: python3 interface.py 1.2.3.4              # test against IP
    # USAGE: python3 interface.py 1.2.3.4 retrieve     # retrieve last 10 ticks (for exploits relying on checker interaction)
    # (or use gamelib/run-checkers to test against docker container)
    team = Team(1, 'TestTeam', sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1')
    service = SaarsecVV(1)

    if len(sys.argv) > 2 and sys.argv[2] == 'retrieve':
        for tick in range(1, 10):
            try:
                service.retrieve_flags(team, tick)
            except:
                pass
        sys.exit(0)

    for tick in range(1, 4):
        print(f'\n\n=== TICK {tick} ===')
        service.check_integrity(team, tick)
        service.store_flags(team, tick)
        service.retrieve_flags(team, tick)

