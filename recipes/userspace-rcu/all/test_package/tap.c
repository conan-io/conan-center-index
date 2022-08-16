/*
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Copyright (C) 2004 Nik Clayton
 * Copyright (C) 2017 Jérémie Galarneau
 */

#define _GNU_SOURCE
#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <assert.h>

#include "tap.h"

static int no_plan = 0;
static int skip_all = 0;
static int have_plan = 0;
static unsigned int test_count = 0; /* Number of tests that have been run */
static unsigned int e_tests = 0; /* Expected number of tests to run */
static unsigned int failures = 0; /* Number of tests that failed */
static char *todo_msg = NULL;
static const char *todo_msg_fixed = "libtap malloc issue";
static int todo = 0;
static int test_died = 0;
static int tap_is_disabled = 0;

/* Encapsulate the pthread code in a conditional.  In the absence of
   libpthread the code does nothing */
#ifdef HAVE_LIBPTHREAD
#include <pthread.h>
static pthread_mutex_t M = PTHREAD_MUTEX_INITIALIZER;
# define LOCK pthread_mutex_lock(&M);
# define UNLOCK pthread_mutex_unlock(&M);
#else
# define LOCK
# define UNLOCK
#endif

static void _expected_tests(unsigned int);
static void _tap_init(void);
static void _cleanup(void);

#ifdef __MINGW32__
static inline
void flockfile (FILE * filehandle) {
       return;
}

static inline
void funlockfile(FILE * filehandle) {
       return;
}
#endif

/*
 * Generate a test result.
 *
 * ok -- boolean, indicates whether or not the test passed.
 * test_name -- the name of the test, may be NULL
 * test_comment -- a comment to print afterwards, may be NULL
 */
unsigned int
_gen_result(int ok, const char *func, const char *file, unsigned int line,
	    const char *test_name, ...)
{
	va_list ap;
	char *local_test_name = NULL;
	char *c;
	int name_is_digits;

	LOCK;

	test_count++;

	/* Start by taking the test name and performing any printf()
	   expansions on it */
	if(test_name != NULL) {
		va_start(ap, test_name);
		if (vasprintf(&local_test_name, test_name, ap) == -1) {
			local_test_name = NULL;
		}
		va_end(ap);

		/* Make sure the test name contains more than digits
		   and spaces.  Emit an error message and exit if it
		   does */
		if(local_test_name) {
			name_is_digits = 1;
			for(c = local_test_name; *c != '\0'; c++) {
				if(!isdigit((unsigned char) *c) && !isspace((unsigned char) *c)) {
					name_is_digits = 0;
					break;
				}
			}

			if(name_is_digits) {
				diag("    You named your test '%s'.  You shouldn't use numbers for your test names.", local_test_name);
				diag("    Very confusing.");
			}
		}
	}

	if(!ok) {
		printf("not ");
		failures++;
	}

	printf("ok %d", test_count);

	if(test_name != NULL) {
		printf(" - ");

		/* Print the test name, escaping any '#' characters it
		   might contain */
		if(local_test_name != NULL) {
			flockfile(stdout);
			for(c = local_test_name; *c != '\0'; c++) {
				if(*c == '#')
					fputc('\\', stdout);
				fputc((int)*c, stdout);
			}
			funlockfile(stdout);
		} else {	/* vasprintf() failed, use a fixed message */
			printf("%s", todo_msg_fixed);
		}
	}

	/* If we're in a todo_start() block then flag the test as being
	   TODO.  todo_msg should contain the message to print at this
	   point.  If it's NULL then asprintf() failed, and we should
	   use the fixed message.

	   This is not counted as a failure, so decrement the counter if
	   the test failed. */
	if(todo) {
		printf(" # TODO %s", todo_msg ? todo_msg : todo_msg_fixed);
		if(!ok)
			failures--;
	}

	printf("\n");

	if(!ok) {
		if(getenv("HARNESS_ACTIVE") != NULL)
			fputs("\n", stderr);

		diag("    Failed %stest (%s:%s() at line %d)",
		     todo ? "(TODO) " : "", file, func, line);
	}
	free(local_test_name);

	UNLOCK;

	/* We only care (when testing) that ok is positive, but here we
	   specifically only want to return 1 or 0 */
	return ok ? 1 : 0;
}

/*
 * Initialise the TAP library.  Will only do so once, however many times it's
 * called.
 */
void
_tap_init(void)
{
	static int run_once = 0;

	if(!run_once) {
		atexit(_cleanup);

		/* stdout needs to be unbuffered so that the output appears
		   in the same place relative to stderr output as it does
		   with Test::Harness */
		setbuf(stdout, 0);
		run_once = 1;
	}
}

/*
 * Note that there's no plan.
 */
int
plan_no_plan(void)
{

	LOCK;

	_tap_init();

	if(have_plan != 0) {
		fprintf(stderr, "You tried to plan twice!\n");
		test_died = 1;
		UNLOCK;
		exit(255);
	}

	have_plan = 1;
	no_plan = 1;

	UNLOCK;

	return 1;
}

/*
 * Note that the plan is to skip all tests
 */
int
plan_skip_all(const char *reason)
{

	LOCK;

	_tap_init();

	skip_all = 1;

	printf("1..0");

	if(reason != NULL)
		printf(" # Skip %s", reason);

	printf("\n");

	UNLOCK;

	exit(0);
}

/*
 * Note the number of tests that will be run.
 */
int
plan_tests(unsigned int tests)
{

	LOCK;

	_tap_init();

	if(have_plan != 0) {
		fprintf(stderr, "You tried to plan twice!\n");
		test_died = 1;
		UNLOCK;
		exit(255);
	}

	if(tests == 0) {
		fprintf(stderr, "You said to run 0 tests!  You've got to run something.\n");
		test_died = 1;
		UNLOCK;
		exit(255);
	}

	have_plan = 1;

	_expected_tests(tests);

	UNLOCK;

	return e_tests;
}

unsigned int
diag(const char *fmt, ...)
{
	va_list ap;

	fputs("# ", stderr);

	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);

	fputs("\n", stderr);

	return 0;
}

unsigned int
rdiag_start(void)
{
	fputs("# ", stderr);
	return 0;
}

unsigned int
rdiag(const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);

	return 0;
}

unsigned int
rdiag_end(void)
{
	fputs("\n", stderr);
	return 0;
}

void
diag_multiline(const char *val)
{
	size_t len, i, line_start_idx = 0;

	assert(val);
	len = strlen(val);

	for (i = 0; i < len; i++) {
		int line_length;

		if (val[i] != '\n') {
			continue;
		}

		assert((i - line_start_idx + 1) <= INT_MAX);
		line_length = i - line_start_idx + 1;
		fprintf(stderr, "# %.*s", line_length, &val[line_start_idx]);
		line_start_idx = i + 1;
	}
}

void
_expected_tests(unsigned int tests)
{

	printf("1..%d\n", tests);
	e_tests = tests;
}

int
skip(unsigned int n, const char *fmt, ...)
{
	va_list ap;
	char *skip_msg = NULL;

	LOCK;

	va_start(ap, fmt);
	if (vasprintf(&skip_msg, fmt, ap) == -1) {
		skip_msg = NULL;
	}
	va_end(ap);

	while(n-- > 0) {
		test_count++;
		printf("ok %d # skip %s\n", test_count,
		       skip_msg != NULL ?
		       skip_msg : "libtap():malloc() failed");
	}

	free(skip_msg);

	UNLOCK;

	return 1;
}

void
todo_start(const char *fmt, ...)
{
	va_list ap;

	LOCK;

	va_start(ap, fmt);
	if (vasprintf(&todo_msg, fmt, ap) == -1) {
		todo_msg = NULL;
	}
	va_end(ap);

	todo = 1;

	UNLOCK;
}

void
todo_end(void)
{

	LOCK;

	todo = 0;
	free(todo_msg);

	UNLOCK;
}

int
exit_status(void)
{
	int r;

	LOCK;

	/* If there's no plan, just return the number of failures */
	if(no_plan || !have_plan) {
		UNLOCK;
		return failures;
	}

	/* Ran too many tests?  Return the number of tests that were run
	   that shouldn't have been */
	if(e_tests < test_count) {
		r = test_count - e_tests;
		UNLOCK;
		return r;
	}

	/* Return the number of tests that failed + the number of tests
	   that weren't run */
	r = failures + e_tests - test_count;
	UNLOCK;

	return r;
}

/*
 * Cleanup at the end of the run, produce any final output that might be
 * required.
 */
void
_cleanup(void)
{

	LOCK;

	if (tap_is_disabled) {
		UNLOCK;
		return;
	}

	/* If plan_no_plan() wasn't called, and we don't have a plan,
	   and we're not skipping everything, then something happened
	   before we could produce any output */
	if(!no_plan && !have_plan && !skip_all) {
		diag("Looks like your test died before it could output anything.");
		UNLOCK;
		return;
	}

	if(test_died) {
		diag("Looks like your test died just after %d.", test_count);
		UNLOCK;
		return;
	}


	/* No plan provided, but now we know how many tests were run, and can
	   print the header at the end */
	if(!skip_all && (no_plan || !have_plan)) {
		printf("1..%d\n", test_count);
	}

	if((have_plan && !no_plan) && e_tests < test_count) {
		diag("Looks like you planned %d %s but ran %d extra.",
		     e_tests, e_tests == 1 ? "test" : "tests", test_count - e_tests);
		UNLOCK;
		return;
	}

	if((have_plan || !no_plan) && e_tests > test_count) {
		diag("Looks like you planned %d %s but only ran %d.",
		     e_tests, e_tests == 1 ? "test" : "tests", test_count);
		UNLOCK;
		return;
	}

	if(failures)
		diag("Looks like you failed %d %s of %d.",
		     failures, failures == 1 ? "test" : "tests", test_count);

	UNLOCK;
}

/* Disable tap for this process. */
void
tap_disable(void)
{
	LOCK;
	tap_is_disabled = 1;
	UNLOCK;
}
