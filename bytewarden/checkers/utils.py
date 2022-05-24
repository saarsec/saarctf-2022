from gamelib import TIMEOUT
from requests import Session
from re import findall
from hashlib import sha256
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from random import choice as rand_choice
from string import ascii_letters, digits

REGEX_2FA_CODE = r"Your new 2FA code is: <strong>(.*?)</strong>"
REGEX_2FA_PREFIX = r'<input type="text" name="prefix" value="(.*?)" hidden>'
REGEX_2FA_DIFF = r'<input type="text" name="difficulty" value="(.*?)" hidden>'

REGEX_QUESTION_QUESTION = r'decrypt_id\("(.*)", ".*", "show_question"\)'
REGEX_PASSWORD_PASSWORD = r'decrypt_id\("(.*)", ".*", "1_pwd"\)'

PORT = 1984

# Returns logged in Session
def register_and_login(ip: str, username: str, password: str) -> Session:

	s = Session()
	creds = {
		"username" : username,
		"password" : password,  # login needs password
		"password1" : password, # register needs password1
	}
	resp = s.post(f"http://{ip}:{PORT}/users/signup/", data = creds, timeout = TIMEOUT)
	#print(username, password)
	#print(resp.text)
	resp = s.post(f"http://{ip}:{PORT}/users/login/" , data = creds, timeout = TIMEOUT)
	
	return s


def encrypt(plaintext: str, password: str) -> str:
	res = b""
	for i in range(len(plaintext)):
		xor = ord(password[i % len(password)]) ^ ord(plaintext[i])
		res += xor.to_bytes(1, "big")

	return b64encode(res)

def decrypt(data: str, password: str) -> str:
	data = b64decode(data)
	res = ""
	for i in range(len(data)):
		xor = ord(password[i % len(password)]) ^ data[i]
		res += chr(xor)

	return res


def post_question(s: Session, ip: str, num: int, question: str, answer: str, password: str, shared: bool = False) -> None:

	question_data = {
		"num"           : str(num),
		"new_question"  : encrypt(question, password),
		"new_answer"    : encrypt(answer, password),
	}
	if shared:
		question_data["is_shared"] = "on"

	resp = s.post(f"http://{ip}:{PORT}/questions/", data = question_data, timeout = TIMEOUT)


def enter_2fa(s: Session, ip: str, code: str):
	
	resp = s.get(f"http://{ip}:{PORT}/vault/", timeout = TIMEOUT)

	# First visit shows 2FA Code and not prompt
	if "Your new 2FA code is: " in resp.text:
		resp = s.get(f"http://{ip}:{PORT}/vault/", timeout = TIMEOUT)

	prefix = findall(REGEX_2FA_PREFIX,  resp.text)[0]
	difficulty = int(findall(REGEX_2FA_DIFF,  resp.text)[0])

	pow_data = {
		"2fa_code": code,
		"pow": compute_pow(prefix, difficulty),
	}
	s.post(f"http://{ip}:{PORT}/vault/", data = pow_data, timeout = TIMEOUT)


def is_valid_pow(digest: str, difficulty: int) -> bool:
	bits = "".join(bin(i)[2:].zfill(8) for i in digest)
	return bits[:difficulty] == "0" * difficulty


def compute_pow(prefix: str, difficulty: int) -> str:
	i = 0
	while True:
		i += 1
		s = prefix + str(i)
		if is_valid_pow(sha256(s.encode()).digest(), difficulty):
			return str(i)
