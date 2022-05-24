#define _GNU_SOURCE

#include "btcstorage.h"
#include <stdio.h>
#include <sys/random.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <fcntl.h>
#include <sys/stat.h>

static FILE *btcfile;
static unsigned int btcfile_pos = 0;

struct BTCStorage {
	unsigned long ts;
	char token[24];
	char data[96];
};

int init_btcstorage() {
	mkdir(".mine", 0777);
	int fd = open(".btcstorage", O_RDWR | O_CREAT, 0600);
	if (fd < 0) return 1;
	btcfile = fdopen(fd, "wb+");
	if (!btcfile) return 1;
	fseek(btcfile, 0, SEEK_END);
	btcfile_pos = ftell(btcfile) % (1024 * 1024 * 4);
	return 0;
}

void btcstorage_get_cmd(struct IncomingMessage *msg, char *data, int len) {
	if (len < 28) return;

	char *response;
	int response_len;
	struct BTCStorage s;
	int offset = *((int *) data);
	if (offset % sizeof(struct BTCStorage) != 0) {
		answerRequest(msg, "Invalid offset", 14);
		return;
	}
	fseek(btcfile, offset, SEEK_SET);
	fread(&s, sizeof(struct BTCStorage), 1, btcfile);
	if (memcmp(data+4, s.token, 24) == 0) {
		response_len = asprintf(&response, "OK. time:%lu btc:%s", s.ts, s.data);
	} else {
		response_len = asprintf(&response, "ERR. Token invalid");
	}

	answerRequest(msg, response, response_len);
	free(response);
}

void btcstorage_set_cmd(struct IncomingMessage *msg, char *data, int len) {
	struct BTCStorage s;
	s.ts = time(NULL);
	getrandom(s.token, sizeof(s.token), 0);
	size_t x = strnlen(data, len);
	if (x > sizeof(s.data) - 1) x = sizeof(s.data) - 1;
	memmove(s.data, data, x);
	s.data[x + 1] = '\0';

	char *response = malloc(1024);
	int response_len = sprintf(response, "OK. time:%lu offset:%d token:", s.ts, btcfile_pos);
	memcpy(response + response_len, s.token, 24);
	response_len += 24;

	fseek(btcfile, btcfile_pos, SEEK_SET);
	fwrite(&s, sizeof(struct BTCStorage), 1, btcfile);
	btcfile_pos = (btcfile_pos + sizeof(struct BTCStorage)) & 0x3fffff;

	answerRequest(msg, response, response_len);
	free(response);
}
