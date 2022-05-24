# pip install twofish
from twofish import Twofish
import binascii


def xor(a: bytes, b: bytes) -> bytes:
	return bytes(x ^ y for x, y in zip(a, b))


def increment(b) -> bytes:
	for i in range(len(b)-1, 0, -1):
		b[i] += 1
		if b[i] != 0:
			break
	return bytes(b)


def decrypt_data(key: bytes, cipher: bytes) -> bytes:
	iv = cipher[:12]
	tag = cipher[-16:]
	ciphertext = cipher[12:-16]
	C = Twofish(key)
	ctr = list(iv+b'\x00\x00\x00\x01')
	plain = b''.join(xor(ciphertext[i:i+16], C.encrypt(increment(ctr))) for i in range(0, len(ciphertext), 16))
	return plain


def check_decryption(fname: str):
	with open(fname, 'rb') as f:
		cipher = f.read()
	print('Cipher-File:', len(cipher), 'bytes')
	key = binascii.unhexlify('d8 45 49 a0 ec 20 eb 23 ed 6d 1e 66 0e 6e b9 71'.replace(' ', ''))
	print(decrypt_data(key, cipher))


if __name__ == '__main__':
	check_decryption('../service/cmake-build-debug/r00t-client/test.txt.enc')

