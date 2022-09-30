/*
 * test_urcu_fork.c
 *
 * Userspace RCU library - test program (fork)
 *
 * Copyright February 2012 - Mathieu Desnoyers <mathieu.desnoyers@efficios.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <assert.h>
#include <sched.h>
#include <errno.h>

#include <urcu/arch.h>
#include <urcu/tls-compat.h>

#ifndef DYNAMIC_LINK_TEST
#define _LGPL_SOURCE
#else
#define rcu_debug_yield_read()
#endif
#include <urcu.h>

#include "tap.h"

/* We generate children 3 levels deep */
#define FORK_DEPTH	3
/* Each generation spawns 10 children */
#define NR_FORK		4

#define NR_TESTS	NR_FORK

static int fork_generation;

/*
 * Only print diagnostic for top level parent process, else the console
 * has trouble formatting the tap output.
 */
#define diag_gen0(...) \
	do { \
		if (!fork_generation) \
			diag(__VA_ARGS__); \
	} while (0)

struct test_node {
	int somedata;
	struct rcu_head head;
};

static void cb(struct rcu_head *head)
{
	struct test_node *node;

	diag_gen0("rcu callback invoked in pid: %d", (int) getpid());
	node = caa_container_of(head, struct test_node, head);
	free(node);
}

static void test_rcu(void)
{
	struct test_node *node;

	rcu_register_thread();

	synchronize_rcu();

	rcu_read_lock();
	rcu_read_unlock();

	node = malloc(sizeof(*node));
	assert(node);

	call_rcu(&node->head, cb);

	synchronize_rcu();

	rcu_unregister_thread();
}

/*
 * Return 0 if child, > 0 if parent, < 0 on error.
 */
static int do_fork(const char *execname)
{
	pid_t pid;

	diag_gen0("%s parent pid: %d, before fork",
		execname, (int) getpid());

	call_rcu_before_fork();
	pid = fork();
	if (pid == 0) {
		/* child */
		fork_generation++;
		tap_disable();

		call_rcu_after_fork_child();
		diag_gen0("%s child pid: %d, after fork",
			execname, (int) getpid());
		test_rcu();
		diag_gen0("%s child pid: %d, after rcu test",
			execname, (int) getpid());
		if (fork_generation >= FORK_DEPTH)
			exit(EXIT_SUCCESS);
		return 0;
	} else if (pid > 0) {
		int status;

		/* parent */
		call_rcu_after_fork_parent();
		diag_gen0("%s parent pid: %d, after fork",
			execname, (int) getpid());
		test_rcu();
		diag_gen0("%s parent pid: %d, after rcu test",
			execname, (int) getpid());
		for (;;) {
			pid = wait(&status);
			if (pid < 0) {
				if (!fork_generation)
					perror("wait");
				return -1;
			}
			if (WIFEXITED(status)) {
				diag_gen0("child %u exited normally with status %u",
					pid, WEXITSTATUS(status));
				if (WEXITSTATUS(status))
					return -1;
				break;
			} else if (WIFSIGNALED(status)) {
				diag_gen0("child %u was terminated by signal %u",
					pid, WTERMSIG(status));
				return -1;
			} else {
				continue;
			}
		}
		return 1;
	} else {
		if (!fork_generation)
			perror("fork");
		return -1;
	}
}

int main(int argc __attribute__((unused)), char **argv)
{
	unsigned int i;

	plan_tests(NR_TESTS);

#if 0
	/* pthread_atfork does not work with malloc/free in callbacks */
	ret = pthread_atfork(call_rcu_before_fork,
		call_rcu_after_fork_parent,
		call_rcu_after_fork_child);
	if (ret) {
		errno = ret;
		perror("pthread_atfork");
		exit(EXIT_FAILURE);
	}
#endif

restart:
	for (i = 0; i < NR_FORK; i++) {
		int ret;

		test_rcu();
		synchronize_rcu();
		ret = do_fork(argv[0]);
		if (!fork_generation) {
			ok(ret >= 0, "child status %d", ret);
		}
		if (ret == 0) {		/* child */
			goto restart;
		} else if (ret < 0) {
			goto error;
		} else {
			/* else parent, continue. */
		}
	}
	if (!fork_generation) {
		return exit_status();
	} else {
		exit(EXIT_SUCCESS);
	}

error:
	if (!fork_generation) {
		return exit_status();
	} else {
		exit(EXIT_FAILURE);
	}
}
