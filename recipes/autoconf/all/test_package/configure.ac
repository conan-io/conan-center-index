# Must init the autoconf setup
# The first parameter is project name
# second is version number
# third is bug report address
AC_INIT([test_package], [1.0])

# Safety checks in case user overwritten --srcdir
AC_CONFIG_SRCDIR([test_package.c])

# Store the auxiliary build tools (e.g., install-sh, config.sub, config.guess)
# in this dir (build-aux)

AC_CONFIG_FILES(Makefile)
AC_CONFIG_HEADER([config.h])

AC_PROG_CC
AC_PROG_CXX

AC_OUTPUT
