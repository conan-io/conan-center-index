AC_INIT([test_package], [1.0])
AC_CONFIG_SRCDIR([test_package.c])
AC_CONFIG_AUX_DIR([autostuff])
AM_INIT_AUTOMAKE([foreign])
AC_PROG_CC
m4_pattern_forbid([^AX_],
        [Unexpanded AX_ macro found. Please install GNU autoconf-archive.])
AX_CXX_BOOL()
AX_CXX_HAVE_VECTOR_AT()
AX_CXX_HAVE_BIND()
AX_PRINTF_SIZE_T()
AX_CHECK_AWK_INDEX()
AX_BERKELEY_DB()
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
