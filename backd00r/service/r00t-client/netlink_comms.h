#ifndef R00T_NETLINK_COMMS_H
#define R00T_NETLINK_COMMS_H

#include <stdint.h>

struct IncomingMessage {
	uint32_t source_ip;
	uint32_t icmp_hdr_info;
	char data[0];
};

typedef void (*IncomingMessageHandler)(struct IncomingMessage *msg, int len);

int init_communication(void);

void handle_incoming_messages(IncomingMessageHandler handler);

void answerRequest(struct IncomingMessage *msg, const char *response, int len);

#endif //R00T_NETLINK_COMMS_H
