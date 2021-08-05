AC_INIT([hello], [1.0])
AC_CONFIG_SRCDIR([hello.c])
AC_CONFIG_AUX_DIR([autostuff])
AM_INIT_AUTOMAKE([foreign])
AC_PROG_CC
m4_pattern_forbid([^AX_],
        [Unexpanded AX_ macro found. Please install GNU autoconf-archive.])
AX_CXX_BOOL()
AC_CONFIG_FILES([Makefile])
AC_OUTPUT

