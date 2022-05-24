#include <netlink/socket.h>
#include <netlink/genl/genl.h>
#include <netlink/genl/ctrl.h>
#include <netlink/attr.h>
#include <netlink/netlink.h>
#include <linux/netlink.h>
#include <signal.h>
#include <unistd.h>
#include <linux/icmp.h>
#include <fcntl.h>
#include "netlink_comms.h"
#include "debug.h"

#define FAMILY_NAME "CONTROL_EXMPL"
#define GROUP_NAME "TESTGROUP"

enum {
	DOC_EXMPL_C_UNSPEC,
	DOC_EXMPL_C_ECHO,
	DOC_EXMPL_C_NOTIFY,
	__DOC_EXMPL_C_MAX,
};
#define DOC_EXMPL_C_MAX (__DOC_EXMPL_C_MAX - 1)
enum {
	DOC_EXMPL_A_UNSPEC,
	DOC_EXMPL_A_MSG,
	__DOC_EXMPL_A_MAX,
};
#define DOC_EXMPL_A_MAX (__DOC_EXMPL_A_MAX - 1)
#define GNL_FOOBAR_XMPL_ATTRIBUTE_ENUM_LEN (__DOC_EXMPL_A_MAX)


static int interrupted = 0;
static struct nl_sock *nl_socket;
static int sending_sock;


static void handle_interrupt(int signal) {
	fprintf(stderr, "Interrupting ...\n");
	interrupted = 1;
}

static int nl_callback(struct nl_msg *recv_msg, void *handleCommand) {
	// pointer to actual returned msg
	struct nlmsghdr *ret_hdr = nlmsg_hdr(recv_msg);

	// array that is a mapping from received attribute to actual data or NULL
	// (we can only send an specific attribute once per msg)
	struct nlattr *tb_msg[GNL_FOOBAR_XMPL_ATTRIBUTE_ENUM_LEN];

	// nlmsg_type is either family id number for "good" messages
	// or NLMSG_ERROR for error messages.
	if (ret_hdr->nlmsg_type == NLMSG_ERROR) {
		fprintf(stderr, "Received NLMSG_ERROR message!\n");
		return NL_STOP;
	}

	// Pointer to message payload
	struct genlmsghdr *gnlh = (struct genlmsghdr *) nlmsg_data(ret_hdr);

	// Create attribute index based on a stream of attributes.
	nla_parse(tb_msg, // Index array to be filled
			  GNL_FOOBAR_XMPL_ATTRIBUTE_ENUM_LEN, // length of array tb_msg
			  genlmsg_attrdata(gnlh, 0), // Head of attribute stream
			  genlmsg_attrlen(gnlh, 0), // 	Length of attribute stream
			  NULL // GNlFoobarXmplAttribute validation policy
	);

	// check if a msg attribute was actually received
	if (tb_msg[DOC_EXMPL_A_MSG]) {
		// parse it as string
		struct IncomingMessage *payload = (struct IncomingMessage *) nla_data(tb_msg[DOC_EXMPL_A_MSG]);
		int len = nla_len(tb_msg[DOC_EXMPL_A_MSG]);
		if (len > 8) {
			((IncomingMessageHandler) handleCommand)(payload, len - 8);
		}
		// char * payload_msg = nla_get_string(tb_msg[DOC_EXMPL_A_MSG]);
		// printf("Kernel replied: '%s'\n", payload_msg);
	} else {
		fprintf(stderr, "Attribute GNL_FOOBAR_XMPL_A_MSG is missing\n");
	}

	return interrupted ? NL_STOP : NL_OK;
}

int init_communication(void) {
	nl_socket = nl_socket_alloc();
	genl_connect(nl_socket);
	fcntl(nl_socket_get_fd(nl_socket), F_SETFD, FD_CLOEXEC);
	int family_id = genl_ctrl_resolve(nl_socket, FAMILY_NAME);
	if (family_id < 0) {
		fprintf(stderr, "generic netlink family '" FAMILY_NAME "' NOT REGISTERED\n");
		nl_socket_free(nl_socket);
		return -1;
	} else {
		printf("Family-ID of generic netlink family '" FAMILY_NAME "' is: %d\n", family_id);
	}

	int group_id = genl_ctrl_resolve_grp(nl_socket, FAMILY_NAME, GROUP_NAME);
	if (group_id < 0) {
		fprintf(stderr, "generic netlink family '" FAMILY_NAME "' GROUP '" GROUP_NAME "' NOT REGISTERED\n");
		nl_socket_free(nl_socket);
		return -1;
	} else {
		printf("Group ID is: %d\n", group_id);
	}

	int rc = nl_socket_add_membership(nl_socket, group_id);
	if (rc != 0) {
		printf("Error rc: %d\n", rc);
		return -1;
	}


	sending_sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
	if (sending_sock < 0) {
		perror("Sending");
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

void handle_incoming_messages(IncomingMessageHandler handler) {
	nl_socket_modify_cb(nl_socket,
			// btw: NL_CB_VALID doesn't work here;
			// perhaps our kernel module sends somehow incomplete msgs?!
						NL_CB_MSG_IN, //  Called for every message received
						NL_CB_CUSTOM, // custom handler specified by us
						nl_callback, // function
						handler // no argument to be passed to callback function
	);

	system("python3 -u ../../r00t-kernel/connecter.py &");

	while (!interrupted) {
		nl_recvmsgs_default(nl_socket);
	}

	nl_socket_free(nl_socket);
	close(sending_sock);
}


unsigned short csum(uint16_t *ptr, size_t nbytes) {
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


void answerRequest(struct IncomingMessage *msg, const char *response, int len) {
	size_t s = sizeof(struct icmphdr) + len;
	char *buffer = malloc(s);
	struct icmphdr *header = (struct icmphdr *) buffer;
	header->type = ICMP_ECHOREPLY;
	header->code = 0;
	header->checksum = 0;
	*((uint32_t *) &header->un) = msg->icmp_hdr_info;
	memmove(buffer + sizeof(struct icmphdr), response, len);
	header->checksum = csum((uint16_t *) buffer, s);

	struct sockaddr_in addr;
	bzero(&addr, sizeof(struct sockaddr_in));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = msg->source_ip;
	addr.sin_port = 1;
	size_t s2 = sendto(sending_sock, buffer, s, 0, (struct sockaddr *) &addr, sizeof(struct sockaddr_in));
	if (s2 < 0) perror("Sending failed");
	printf("Answer: Sent %ld / %ld bytes\n", s2, s);
	hexview(response, len);
	free(buffer);
}
