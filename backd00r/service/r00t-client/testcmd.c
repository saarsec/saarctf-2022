#include <stdio.h>
#include "testcmd.h"
#include "debug.h"

extern char current_packet[2048];
extern char SECRET_KEY[16];

void testcmd(struct IncomingMessage *msg, char *data, int len) {
	int s1len = data[0];
	printf("start of packet=%p  msg->data=%p  s1len=%d  start=%p  len=%d\n", current_packet, msg->data, s1len, msg->data + 1 + s1len, len - 1 - s1len);

	if (len == 0 || s1len >= len) {
		answerRequest(msg, "Invalid request", 15);
		return;
	}

	printf("String 1 (as string): %.*s\n", s1len, data+1);
	hexview(data+1, s1len);
	printf("String 2:\n");
	hexview(data+1+s1len, len-s1len-1);
	printf("Secret key:\n");
	hexview(SECRET_KEY, 16);

	//answerRequest(msg, data + 1 + s1len, len - 1 - s1len);
	answerRequest(msg, "OK", 2);
}
