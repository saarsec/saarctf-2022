#ifndef R00T_RAW_SOCKET_COMMS_H
#define R00T_RAW_SOCKET_COMMS_H

#include <stdint.h>
#include <linux/icmp.h>
#include <linux/ip.h>

struct __attribute__((packed)) IncomingMessage {
	struct icmphdr icmp;
	uint32_t ping_identifier_data;
	char data[0];
};

typedef void (*IncomingMessageHandler)(struct IncomingMessage *msg, int len);

int init_communication(void);

void handle_incoming_messages(IncomingMessageHandler handler);

void answerRequest(struct IncomingMessage *msg, const char *response, int len);

#endif //R00T_RAW_SOCKET_COMMS_H
