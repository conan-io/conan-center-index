AC_PREREQ([2.69])
AC_CONFIG_AUX_DIR([build-aux])
AC_INIT([test_package], [1.0])
AC_CONFIG_SRCDIR([configure.ac])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

m4_ifndef([XORG_MACROS_VERSION],[
    m4_fatal([must install xorg-macros 1.1 or later before running autoconf/autogen])],[
    AC_MSG_NOTICE([xorg-macros version ok])])

XORG_MACROS_VERSION([1.1])

AC_CONFIG_FILES(Makefile)
AC_OUTPUT
