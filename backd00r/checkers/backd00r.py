import binascii
import os
import sys
import random
import time
from collections import defaultdict
from typing import Callable, Dict

from gamelib import *
try:
    from .connector import BackdoorConnector
    from .utils_crypto import decrypt_data
except ImportError:
    from connector import BackdoorConnector
    from utils_crypto import decrypt_data

os.environ['PWNLIB_NOTERM'] = '1'
from pwn import asm, context, p64
context.arch = 'amd64'


def clamp(x: int) -> int:
    return x & 0xffffffffffffffff


def clamp_signed(x: int) -> int:
    x = x & 0xffffffffffffffff
    if x >= 0x8000000000000000:
        x -= 0x10000000000000000
    return x


def is_32_bit(x: int) -> int:
    return -0x80000000 <= x <= 0x7fffffff


def random_constant() -> int:
    r = random.randint(0, 3)
    if r == 0:
        return random.randint(-0x7f, 0x7f)
    if r == 1:
        return random.randint(-0x7fff, 0x7fff)
    if r == 2:
        return random.randint(-0x7fffffff, 0x7fffffff)
    return random.randint(-0x8000000000000000, 0x7fffffffffffffff)


def random_constant_32() -> int:
    r = random.randint(0, 2)
    if r == 0:
        return random.randint(-0x7f, 0x7f)
    if r == 1:
        return random.randint(-0x7fff, 0x7fff)
    return random.randint(-0x7fffffff, 0x7fffffff)


class MiningCodeGen:
    INIT_REG = [
        lambda x: (r := random.randint(0, 0x100), f'mov {x}, {r}'),
        lambda x: (r := random.randint(-0xffff, 0xffff), f'mov {x}, {r}'),
        lambda x: (r := random.randint(-0xffffffff, 0xffffffff), f'mov {x}, {r}'),
        lambda x: (r := random.randint(-0x7fffffffffffffff, 0x7fffffffffffffff), f'mov {x}, {r}'),
        lambda x: (0, f'xor {x}, {x}'),
    ]

    def __init__(self):
        self.code: List[str] = []
        self.output = b''
        self.values: Dict[str, Optional[int]] = defaultdict(lambda: None)
        self.ARITH_INSTRUCTIONS = [
            lambda: (2, 0, 'add {}, {}', lambda *x: (self.values[x[0]] + self.values[x[1]])),
            lambda: (2, 0, 'sub {}, {}', lambda *x: (self.values[x[0]] - self.values[x[1]])),
            lambda: (2, 0, 'and {}, {}', lambda *x: (self.values[x[0]] & self.values[x[1]])),
            lambda: (2, 0, 'or {}, {}', lambda *x: (self.values[x[0]] | self.values[x[1]])),
            lambda: (2, 0, 'mov {}, {}', lambda *x: (self.values[x[1]])),

            lambda: (2, r := random_constant_32(), f'add {{}}, {r}', lambda *x: (self.values[x[0]] + r)),
            lambda: (2, r := random_constant_32(), f'sub {{}}, {r}', lambda *x: (self.values[x[0]] - r)),
            lambda: (2, r := random_constant_32(), f'and {{}}, {r}', lambda *x: (self.values[x[0]] & r)),
            lambda: (2, r := random_constant_32(), f'or {{}}, {r}', lambda *x: (self.values[x[0]] | r)),
            lambda: (2, r := random_constant_32(), f'mov {{}}, {r}', lambda *x: r),

            lambda: (1, 0, 'inc {}', lambda *x: (self.values[x[0]] + 1)),
            lambda: (1, 0, 'dec {}', lambda *x: (self.values[x[0]] - 1)),
            lambda: (1, 0, 'neg {}', lambda *x: (-self.values[x[0]])),
            lambda: (1, 0, 'not {}', lambda *x: (~self.values[x[0]])),
            lambda: (1, r := random.randint(1, 31), f'shl {{}}, {r}', lambda *x: (self.values[x[0]] << r)),
            lambda: (1, r := random.randint(1, 31), f'shr {{}}, {r}', lambda *x: (clamp(self.values[x[0]]) >> r)),
            lambda: (1, r := random.randint(1, 31), f'sar {{}}, {r}', lambda *x: (clamp_signed(self.values[x[0]]) >> r)),
            lambda: (1, r := random.randint(1, 63), f'rol {{}}, {r}', lambda *x: (clamp(self.values[x[0]]) << r | clamp(self.values[x[0]]) >> (64-r))),
            lambda: (1, r := random.randint(1, 63), f'ror {{}}, {r}', lambda *x: (clamp(self.values[x[0]]) >> r | clamp(self.values[x[0]]) << (64-r))),

            lambda: (3, (r1 := random.choice([1,2,4,8]), r2 := random.randint(0, 0xffff)), f'lea {{}}, [{{}}+{{}}*{r1}+{r2}]', lambda *x: self.values[x[1]]+self.values[x[2]]*r1+r2),
        ]
        # lea

    def assemble(self) -> bytes:
        return asm('\n'.join(self.code))

    def debug(self):
        print('=== CODE ===')
        print('\n'.join(self.code))
        print('OUTPUT: ', self.output)

    def generate(self):
        available_regs = ['rax', 'rbx', 'rcx', 'rdx', 'rdi', 'rsi', 'r8', 'r9', 'r10', 'r11', 'r12', 'rbp', 'qword ptr [rsp]', 'qword ptr [rsp+8]']
        random.shuffle(available_regs)
        for reg in available_regs[:random.randint(5, 8)]:
            self.values[reg] = None

        for s, regs, cb in self.gen_instructions(random.randint(5, 15)):
            self.init_all(regs)
            self.code.append(s)
            self.values[regs[0]] = cb(*regs)

        r = random.randint(0, 100)
        if r < 40:
            self.gen_ifelse()
        elif r < 80:
            self.gen_for()
        else:
            self.output_registers([r for r, v in self.values.items() if r[0] != 'q' and v is not None])

        for s, regs, cb in self.gen_instructions(random.randint(5, 15)):
            self.init_all(regs)
            self.code.append(s)
            self.values[regs[0]] = cb(*regs)

        if random.randint(0, 100) < 50:
            r = random.randint(0, 100)
            if r < 40:
                self.gen_ifelse()
            elif r < 80:
                self.gen_for()
            else:
                self.output_registers([r for r, v in self.values.items() if r[0] != 'q' and v is not None])

            for s, regs, cb in self.gen_instructions(random.randint(5, 15)):
                self.init_all(regs)
                self.code.append(s)
                self.values[regs[0]] = cb(*regs)

        self.output_registers([r for r, v in self.values.items() if v is not None])
        self.code.append('ud2')

    def gen_instructions(self, n: int) -> List[Tuple[str, List[str], Callable]]:
        instructions = []
        for _ in range(n):
            num_args, _, ins, cb = random.choice(self.ARITH_INSTRUCTIONS)()
            regs = [random.choice(list(self.values)) for _ in range(num_args)]
            while len(regs) == 2 and regs[0][0] == 'q' and regs[1][0] == 'q':
                regs = [random.choice(list(self.values)) for _ in range(num_args)]
            if ins.startswith('lea '):
                regs = [random.choice([k for k in self.values if k[0] != 'q']) for _ in range(num_args)]
            instructions.append((ins.format(*regs), regs, cb))
        return instructions

    def gen_ifelse(self):
        initialized_regs = [k for k, v in self.values.items() if v is not None]
        reg = random.choice(initialized_regs)
        value = clamp_signed(self.values[reg])
        rnd = random_constant_32()
        label = f'lbl{random.randint(0, 1000000)}'
        possible_conditions = [
            (f'cmp {reg}, {value} ; je {label}' if is_32_bit(value) else f'mov r13, {value} ; cmp {reg}, r13 ; je {label}', True),
            (f'cmp {reg}, {value} ; jne {label}' if is_32_bit(value) else f'mov r13, {value} ; cmp {reg}, r13 ; jne {label}', False),
            (f'cmp {reg}, {rnd} ; je {label}', value == rnd),
            (f'cmp {reg}, {rnd} ; jne {label}', value != rnd),
            (f'cmp {reg}, {rnd} ; ja {label}', clamp(value) > clamp(rnd)),
            (f'cmp {reg}, {rnd} ; jb {label}', clamp(value) < clamp(rnd)),
            (f'cmp {reg}, {rnd} ; jge {label}', value >= rnd),
            (f'cmp {reg}, {rnd} ; jl {label}', value < rnd),
        ]
        c, jt = random.choice(possible_conditions)
        self.code.append(c)
        for s, regs, cb in self.gen_instructions(random.randint(3, 10)):
            if not jt:
                self.init_all(regs)
            self.code.append(s)
            if not jt:
                self.values[regs[0]] = cb(*regs)
        self.code.append(f'jmp {label}end')
        self.code.append(f'{label}:')
        for s, regs, cb in self.gen_instructions(random.randint(3, 10)):
            if jt:
                self.init_all(regs)
            self.code.append(s)
            if jt:
                self.values[regs[0]] = cb(*regs)
        self.code.append(f'{label}end:')

    def gen_for(self):
        # gen body, init all its values
        body = self.gen_instructions(random.randint(3, 15))
        regs_for_body = set()
        for s, regs, cb in body:
            for r in regs:
                regs_for_body.add(r)
        self.init_all(list(regs_for_body))

        # build assembly loop
        label = f'forlabel{random.randint(0, 1000000)}'
        iterations = random.randint(1, 10)
        ireg = random.choice(['r13', 'r14', 'r15'])
        self.code.append(f'mov {ireg}, {iterations}')
        self.code.append(f'{label}:')
        for s, regs, cb in body:
            self.code.append(s)
        self.code.append(f'dec {ireg}')
        self.code.append(f'jnz {label}')

        # execute body for our values <iterations> times
        for _ in range(iterations):
            for s, regs, cb in body:
                self.values[regs[0]] = cb(*regs)

    def init_all(self, regs: List[str]):
        for reg in regs:
            if reg in self.values and self.values[reg] is not None:
                continue
            if reg[0] == 'q':
                initialized_regs = [k for k, v in self.values.items() if v is not None]
                if len(initialized_regs) == 0:
                    self.init_all(['rax'])
                    initialized_regs = [k for k, v in self.values.items() if v is not None]
                r = random.choice(initialized_regs)
                self.code.append(f'push {r}')
                self.values['qword ptr [rsp+8]'] = self.values[r]
                r = random.choice(initialized_regs)
                self.code.append(f'push {r}')
                self.values['qword ptr [rsp]'] = self.values[r]
                continue
            v, c = random.choice(self.INIT_REG)(reg)
            self.values[reg] = v
            self.code.append(c)

    def output_registers(self, regs: List[str]):
        num_pushes = 0
        for r in regs:
            if r[0] == 'q':
                r = self.offset_correction(r, num_pushes * 8)
                self.code.append(f'mov r13, {r} ; push r13')
            else:
                self.code.append(f'push {r}')
            num_pushes += 1
        self.code.append(f'mov rax, 1 ; mov rdi, 1 ; mov rsi, rsp ; mov rdx, {len(regs) * 8} ; syscall')
        self.output += b''.join(p64(self.values[r] & 0xffffffffffffffff) for r in regs[::-1])
        for r in regs[::-1]:
            if r[0] == 'q':
                self.code.append(f'pop r13')
            else:
                self.code.append(f'pop {r}')
        if 'rax' not in regs:
            self.values['rax'] = len(regs) * 8
        if 'rdi' not in regs:
            self.values['rdi'] = 1
        if 'rsi' not in regs and 'rsi' in self.values:
            self.values['rsi'] = None
        if 'rdx' not in regs:
            self.values['rdx'] = len(regs) * 8

    def offset_correction(self, reg: str, offset: int) -> str:
        if '+' in reg:
            a, b = reg.split('+')
            return a + '+' + str(int(b[:-1]) + offset) + ']'
        return reg[:-1] + f'+{offset}]'




class BackdoorInterface(ServiceInterface):
    name = 'backd00r'
    flag_id_types = ['alphanum20']

    def check_integrity(self, team: Team, tick: int):
        with BackdoorConnector(team.ip, True, gamelib.OfflineException) as connector:
            pong = connector.command(b'PING\x00', 3.0, 2)
            if not pong:
                raise OfflineException('Service does not respond')
            assert pong == b'PONG', 'PONG'
        return True

    def store_flags(self, team: Team, tick: int) -> int:
        with BackdoorConnector(team.ip, True, gamelib.OfflineException) as connector:
            # store flag1 in btc storage
            flag1 = self.get_flag(team, tick, 0)
            response = connector.check_command(b'SET_BTC_ADDRESS\x00' + flag1.encode())
            # "OK. time:%lu offset:%d token:%.24s"
            assert response.startswith(b'OK. '), 'SET_BTC_ADDRESS invalid response'
            response = response.split(b' ', 3)
            assert len(response) == 4, 'SET_BTC_ADDRESS invalid response'
            assert response[2].startswith(b'offset:'), 'SET_BTC_ADDRESS invalid response'
            offset = int(response[2][7:].decode())
            assert response[3].startswith(b'token:'), 'SET_BTC_ADDRESS invalid response'
            token = response[3][6:]
            assert len(token) == 24, 'SET_BTC_ADDRESS invalid token'
            self.store(team, tick, 'btc', [offset, binascii.hexlify(token).decode()])
            print('')

            # store flag2 in file and encrypt it
            flag2 = self.get_flag(team, tick, 1)
            filename = (self.get_flag_id(team, tick) + ".txt").encode()
            response = connector.check_command(b'RANSOM_MESSAGE\x00' + bytes([len(filename)]) + filename + flag2.encode())
            if response == b'File open failed':
                some_key = self.load(team, tick, 'key')
                if not some_key:
                    raise AssertionError('RANSOM_MESSAGE failed (File open failed)')
            else:
                assert response == b'OK', 'RANSOM_MESSAGE failed'
                response = connector.check_command(b'RANSOM_ENCRYPT\x00' + filename)
                if response == b'File open failed':
                    some_key = self.load(team, tick, 'key')
                    if not some_key:
                        raise AssertionError('RANSOM_MESSAGE failed (File open failed)')
                else:
                    assert response.startswith(b'OK. key='), 'RANSOM_ENCRYPT failed'
                    assert len(response) == 24, 'RANSOM_ENCRYPT invalid response length'
                    self.store(team, tick, 'key', binascii.hexlify(response[8:]).decode())
            print('')

            codegen = MiningCodeGen()
            codegen.generate()
            codegen.debug()
            response = connector.check_command(b'MINE\x00' + codegen.assemble(), TIMEOUT)
            if len(response) == 0 and len(codegen.output) > 0:
                raise MumbleException('MINE did not output anything')
            assert response == codegen.output, 'MINE output wrong'

            print('')
        return 2

    def retrieve_flags(self, team: Team, tick: int) -> int:
        try:
            offset, token = self.load(team, tick, 'btc')
        except:
            raise FlagMissingException('Flag1 never stored')
        try:
            key = binascii.unhexlify(self.load(team, tick, 'key'))
        except:
            raise FlagMissingException('Flag1 never stored')

        with BackdoorConnector(team.ip, True, gamelib.OfflineException) as connector:
            # retrieve flag1
            flag1 = self.get_flag(team, tick, 0)
            response = connector.check_command(b'GET_BTC_ADDRESS\x00' + struct.pack('I', offset) + binascii.unhexlify(token))
            assert response.startswith(b'OK. '), 'GET_BTC_ADDRESS invalid response'
            if not response.endswith(flag1.encode()):
                raise FlagMissingException('Flag1 not found in response')
            print('')

            # retrieve flag2
            flag2 = self.get_flag(team, tick, 1)
            filename = (self.get_flag_id(team, tick) + ".txt").encode()
            if (team.id + tick) % 2 == 0:
                # v1: send decrypt command
                for _ in range(random.randint(0, 2)):
                    # test wrong key
                    print('... check invalid key ...')
                    random_key = os.urandom(16)
                    response = connector.check_command(b'RANSOM_DECRYPT\x00' + random_key + filename)
                    assert response == b'Key is wrong', 'Invalid key was not detected'
                print('... check correct key ...')
                response = connector.check_command(b'RANSOM_DECRYPT\x00' + key + filename)
                if response != flag2.encode():
                    raise FlagMissingException("Flag2 could not be retrieved (using decrypt)")
            else:
                # v2: steal encrypted file, and decrypt locally
                response = connector.check_command(b'STEAL\x00'+filename+b'.enc')
                decrypted = decrypt_data(key, response)
                print('decrypted=', decrypted)
                if decrypted != flag2.encode():
                    raise FlagMissingException("Flag2 could not be retrieved & decrypted (using steal)")
            print('')

        return 2


def test_codegen(team, n):
    largest = 0
    largest_output = 0
    longest_time = 0
    with BackdoorConnector(team.ip, True, gamelib.OfflineException) as connector:
        for _ in range(n):
            t = time.time()
            codegen = MiningCodeGen()
            codegen.generate()
            codegen.debug()
            binary = codegen.assemble()
            t = time.time() - t
            print('Assembled: ', len(binary), 'bytes in ', t, 'seconds')
            largest = max(largest, len(binary))
            largest_output = max(largest_output, len(codegen.output))
            longest_time = max(longest_time, t)
            response = connector.check_command(b'MINE\x00' + binary)
            print(codegen.output)
            print(response)
            print(response == codegen.output)
            assert response == codegen.output
    print('Largest code:  ', largest, 'bytes')
    print('Largest output:', largest_output, 'bytes')
    print('Longest time:  ', longest_time, 'seconds')


if __name__ == '__main__':
    if os.getuid() == 1000:
        cmd = ['/usr/bin/sudo', 'python3', '-u'] + sys.argv
        if 'PYTHONPATH' in os.environ:
            cmd = ['/usr/bin/sudo', 'PYTHONPATH='+os.environ['PYTHONPATH'], 'python3', '-u'] + sys.argv
        os.execv('/usr/bin/sudo', cmd)

    # USAGE: python3 interface.py                      # test against localhost
    # USAGE: python3 interface.py 1.2.3.4              # test against IP
    # USAGE: python3 interface.py 1.2.3.4 retrieve     # retrieve last 10 ticks (for exploits relying on checker interaction)
    # (or use gamelib/run-checkers to test against docker container)
    team = Team(1, 'TestTeam', sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1')
    service = BackdoorInterface(1)

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

