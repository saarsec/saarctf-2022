// musl-gcc -static -Os -flto -s selenium_wrapper.c -o selenium_wrapper

#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>


/**
 * Wrapper for selenium processes, ensuring proper termination (even if the invoking process crashes or hangs).
 * After a timeout (in seconds), the selenium (and chromium) processes are terminated using SIGTERM. 
 * If this is not successful, a SIGKILL is delivered 2 seconds later.
 * Termination process starts once this process receives a terminating signal, its parent process terminates or the countdown is over.
 */


#define VERBOSE 0
#define LOGFILE 0


pid_t child_pid = 0;
int do_soft_interrupt = 1;


void enforce_termination(int signum) {
	if (VERBOSE) fprintf(stderr, "Received signal %d ...\n", signum);
	if (!child_pid) return;
	if (do_soft_interrupt) {
		if (VERBOSE) fprintf(stderr, "trying soft terminate\n");
		kill(-child_pid, SIGTERM);
		do_soft_interrupt = 0;
		alarm(2);
	} else {
		if (VERBOSE) fprintf(stderr, "trying hard terminate\n");
		kill(-child_pid, SIGKILL);
		signal(SIGALRM, SIG_DFL);
		alarm(2);
	}
}

void child_handler(int sig) {
	pid_t pid;
	int status;
	while((pid = waitpid(-1, &status, WNOHANG)) > 0) {
		if (pid == child_pid) {
			if (VERBOSE) fprintf(stderr, "child %d terminated => exit with %d\n", pid, status);
			exit(status);
		} else {
			if (VERBOSE) fprintf(stderr, "child %d terminated with %d\n", pid, status);
		}
	}
}

int main(int argc, char*const argv[]) {
	if (argc < 3) {
		fprintf(stderr, "USAGE: %s <timeout in seconds> <program> [<argument> ...]\n", argv[0]);
		return 1;
	}
	int deadline = atoi(argv[1]);
	if (deadline <= 0) return 1;

	signal(SIGINT, enforce_termination);
	signal(SIGTERM, enforce_termination);
	signal(SIGQUIT, enforce_termination);
	signal(SIGALRM, enforce_termination);
	signal(SIGCHLD, child_handler);
	prctl(PR_SET_PDEATHSIG, SIGTERM);
	prctl(PR_SET_CHILD_SUBREAPER, 1);
	alarm(deadline);

	child_pid = fork();
	if (child_pid < 0) {
		perror("fork failed");
	} else if (child_pid > 0) {
		// wait for children
		close(STDIN_FILENO);
		while (1) {
			pause();
		}
	} else {
		if (LOGFILE) {
			char *fname;
			asprintf(&fname, "/dev/shm/chrome_%d.log", getpid());
			int fd = open(fname, O_WRONLY|O_APPEND|O_CREAT, 0644);
			fprintf(stderr, "fname = \"%s\"  fd=%d\n", fname, fd);
			dup2(fd, STDOUT_FILENO);
			dup2(fd, STDERR_FILENO);
			close(fd);
		}

		// run child process
		if (VERBOSE) fprintf(stderr, "Subprocess is ready: pid %d\n", getpid());
		prctl(PR_SET_PDEATHSIG, SIGTERM);
		if (setpgid(0, 0) != 0) {
			perror("setpgid");
			return 1;
		}
		execv(argv[2], argv + 2);
		perror("execve failed");
	}
	return 1;
}
