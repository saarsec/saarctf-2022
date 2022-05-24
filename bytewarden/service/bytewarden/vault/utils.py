from random import choice as rand_choice
from string import digits, hexdigits
from bytewarden.settings import POW_DIFFICULTY, TWOFA_LENGTH
from hashlib import sha256

ZEROS = '0' * POW_DIFFICULTY


def random_string(charset, length):
	return "".join(rand_choice(charset) for _ in range(length))


def random_code():
	return random_string(digits, TWOFA_LENGTH)

def set_code(user):
	user.code = random_code()
	user.save()

def two_factor_match(u_code, entered):

	for i in range(TWOFA_LENGTH):
		if u_code[i] != entered[i] or type(u_code[i]) != type(entered[i]):
			return False

	return True

def get_pow_prefix():
	return random_string(hexdigits, POW_DIFFICULTY)

def pow_valid(prefix, pow_str):
	
	digest = sha256((prefix + pow_str).encode()).digest()
	bits = "".join(bin(i)[2:].zfill(8) for i in digest)

	return bits[:POW_DIFFICULTY] == ZEROS