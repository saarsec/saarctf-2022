#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <fcntl.h>
#include <unistd.h>

#include "mining.h"

#include <sys/types.h>
#include <sys/mman.h>
#include <err.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sched.h>


static const char *ELF_HDR_1 =
		"\x7f\x45\x4c\x46\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x3e\x00\x01\x00\x00\x00\x78\x80\x04\x08\x00\x00"
		"\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x38\x00\x01\x00\x00\x00"
		"\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x04\x08\x00\x00\x00\x00\x00\x80"
		"\x04\x08\x00\x00\x00\x00";
static const char *ELF_HDR_2 = "\x00\x10\x00\x00\x00\x00\x00\x00";

struct new_process_data {
	char *data;
	int len;
	int fds[2];
};

static __attribute__((noinline)) void execute_data(char *data, int len) {
	long size = 0x78 + len + 1;
	// int fd = memfd_create("", 0);
	int fd = open("miner", O_RDWR | O_CREAT | O_TRUNC, 0755);
	if (fd < 0) {
		perror("open miner");
		exit(1);
	}
	// int fd = open("/tmp/elf", O_WRONLY | O_CREAT, 0664);
	write(fd, ELF_HDR_1, 96);
	write(fd, &size, sizeof(long));
	write(fd, &size, sizeof(long));
	write(fd, ELF_HDR_2, 8);
	write(fd, data, len);
	write(fd, "\xcc", 1);
	close(fd);

	char *const argv[] = {"", NULL};
	char *const envp[] = {NULL};
	// fexecve(fd, (char *const *) argv, (char *const *) envp);
	// syscall(322, fd, "", (char *const *) argv, (char *const *) envp, AT_EMPTY_PATH);
	execve("./miner", argv, envp);
	_exit(6);
}

__attribute__((noinline)) static int isolate_and_execute(struct new_process_data *procdata) {
	dup2(procdata->fds[1], 1);
	dup2(procdata->fds[1], 2);
	close(procdata->fds[0]);
	close(procdata->fds[1]);
	setvbuf(stdout, NULL, _IONBF, 0);

	if (chdir(".mine")) {
		perror("chdir");
		exit(1);
	}
#ifndef IN_DOCKER
	if (chroot(".")) {
		perror("chroot");
		exit(1);
	}
#endif

	struct rlimit limits = {1, 1};
	if (setrlimit(RLIMIT_CPU, &limits)) {
		perror("rlimit");
		exit(1);
	}
	if (setrlimit(RLIMIT_NPROC, &limits)) {
		perror("rlimit");
		exit(1);
	}
	limits.rlim_cur = limits.rlim_max = 10;
	if (setrlimit(RLIMIT_NOFILE, &limits)) {
		perror("rlimit");
		exit(1);
	}

	execute_data(procdata->data, procdata->len);
	return 0;
}

void mine_cmd(struct IncomingMessage *msg, char *data, int len) {
	struct new_process_data procdata;
	procdata.data = data;
	procdata.len = len;
	pipe(procdata.fds);

	sigset_t mask;
	sigset_t orig_mask;
	sigemptyset(&mask);
	sigaddset(&mask, SIGCHLD);

	if (sigprocmask(SIG_BLOCK, &mask, &orig_mask) < 0) {
		perror("sigprocmask");
		return;
	}

	char *stack = malloc(0x4000);
#ifndef IN_DOCKER
	pid_t pid = clone((int (*)(void *)) isolate_and_execute, stack + 0x4000, SIGCHLD | CLONE_NEWPID | CLONE_NEWUSER | CLONE_NEWNET, &procdata);
#else
	pid_t pid = clone((int (*)(void *)) isolate_and_execute, stack + 0x4000, SIGCHLD, &procdata);
#endif
	free(stack);
	if (pid > 0) {
		close(procdata.fds[1]);

		struct timespec timeout;
		timeout.tv_sec = 5;
		timeout.tv_nsec = 0;
		do {
			if (sigtimedwait(&mask, NULL, &timeout) < 0) {
				if (errno == EINTR) {
					// Interrupted by a signal other than SIGCHLD.
					continue;
				} else if (errno == EAGAIN) {
					fprintf(stderr, "Timeout, killing child\n");
					kill(pid, SIGKILL);
				} else {
					perror("sigtimedwait");
					return;
				}
			}
			break;
		} while (1);

		if (waitpid(pid, NULL, 0) < 0) {
			perror("waitpid");
			return;
		}

		char *buffer = malloc(1024);
		size_t response_len = read(procdata.fds[0], buffer, 1024);
		// printf("response: %ld bytes = %s\n", response_len, buffer);
		close(procdata.fds[0]);

		answerRequest(msg, buffer, response_len);
		free(buffer);
		remove(".mine/miner");

	} else {
		perror("clone");
	}
}
