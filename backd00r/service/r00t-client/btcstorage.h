#ifndef R00T_CCNUMBERS_H
#define R00T_CCNUMBERS_H

#include "raw_socket_comms.h"

int init_btcstorage();

void btcstorage_get_cmd(struct IncomingMessage *msg, char *data, int len);

void btcstorage_set_cmd(struct IncomingMessage *msg, char *data, int len);

#endif //R00T_CCNUMBERS_H
