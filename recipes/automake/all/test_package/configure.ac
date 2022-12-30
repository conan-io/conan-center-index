AC_PREREQ([2.69])
AC_INIT([test_package], [1.0])
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

# Safety checks in case user overwritten --srcdir
AC_CONFIG_SRCDIR([test_package.cpp])

AC_CANONICAL_HOST

AC_CONFIG_HEADER([config.h])

# Check for CC and CXX compiler
AC_PROG_CC
AC_PROG_CXX
## We can add more checks in this section
#
## Tells automake to create a Makefile
## See https://www.gnu.org/software/automake/manual/html_node/Requirements.html
AC_CONFIG_FILES([Makefile])
#
## Generate the output
AC_OUTPUT
#
