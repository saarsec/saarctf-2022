#ifndef R00T_DEBUG_H
#define R00T_DEBUG_H

#include <stdio.h>

static void hexview(const char *response, int len) {
	for (int i = 0; i < len; i++) {
		if (i % 16 == 0) printf("%p  ", response + i);
		printf("%02hhx ", response[i]);
		if (i % 16 == 7) printf(" ");
		if (i % 16 == 15) printf("\n");
	}
	if (len % 16 != 0) printf("\n");
}

#endif //R00T_DEBUG_H
