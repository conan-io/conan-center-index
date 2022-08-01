/*
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Copyright (C) 2004 Nik Clayton
 * Copyright (C) 2017 Jérémie Galarneau
 */

/* '## __VA_ARGS__' is a gcc'ism. C99 doesn't allow the token pasting
   and requires the caller to add the final comma if they've ommitted
   the optional arguments */
#ifdef __GNUC__
# define ok(e, test, ...) ((e) ?					\
			   _gen_result(1, __func__, __FILE__, __LINE__,	\
				       test, ## __VA_ARGS__) :		\
			   _gen_result(0, __func__, __FILE__, __LINE__,	\
				       test, ## __VA_ARGS__))

# define ok1(e) ((e) ?							\
		 _gen_result(1, __func__, __FILE__, __LINE__, "%s", #e) : \
		 _gen_result(0, __func__, __FILE__, __LINE__, "%s", #e))

# define pass(test, ...) ok(1, test, ## __VA_ARGS__);
# define fail(test, ...) ok(0, test, ## __VA_ARGS__);

# define skip_start(test, n, fmt, ...)			\
	do {						\
		if((test)) {				\
			skip(n, fmt, ## __VA_ARGS__);	\
			continue;			\
		}
#elif __STDC_VERSION__ >= 199901L /* __GNUC__ */
# define ok(e, ...) ((e) ?						\
		     _gen_result(1, __func__, __FILE__, __LINE__,	\
				 __VA_ARGS__) :				\
		     _gen_result(0, __func__, __FILE__, __LINE__,	\
				 __VA_ARGS__))

# define ok1(e) ((e) ?							\
		 _gen_result(1, __func__, __FILE__, __LINE__, "%s", #e) : \
		 _gen_result(0, __func__, __FILE__, __LINE__, "%s", #e))

# define pass(...) ok(1, __VA_ARGS__);
# define fail(...) ok(0, __VA_ARGS__);

# define skip_start(test, n, ...)			\
	do {						\
		if((test)) {				\
			skip(n,  __VA_ARGS__);		\
			continue;			\
		}
#else /* __STDC_VERSION__ */
# error "Needs gcc or C99 compiler for variadic macros."
#endif /* __STDC_VERSION__ */

#define skip_end() } while(0);

#ifdef __MINGW_PRINTF_FORMAT
# define TAP_PRINTF_FORMAT __MINGW_PRINTF_FORMAT
#else
# define TAP_PRINTF_FORMAT printf
#endif

__attribute__((format(TAP_PRINTF_FORMAT, 5, 6)))
unsigned int _gen_result(int, const char *, const char *, unsigned int, const char *, ...);

int plan_no_plan(void);
__attribute__((noreturn))
int plan_skip_all(const char *);
int plan_tests(unsigned int);

__attribute__((format(TAP_PRINTF_FORMAT, 1, 2)))
unsigned int diag(const char *, ...);
void diag_multiline(const char *);

__attribute__((format(TAP_PRINTF_FORMAT, 2, 3)))
int skip(unsigned int, const char *, ...);

__attribute__((format(TAP_PRINTF_FORMAT, 1, 2)))
void todo_start(const char *, ...);
void todo_end(void);

int exit_status(void);

void tap_disable(void);

unsigned int rdiag_start(void);
__attribute__((format(TAP_PRINTF_FORMAT, 1, 2)))
unsigned int rdiag(const char *fmt, ...);
unsigned int rdiag_end(void);
