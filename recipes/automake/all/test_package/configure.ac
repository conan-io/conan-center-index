# Must init the autoconf setup
# The first parameter is project name
# second is version number
# third is bug report address
AC_INIT([test_package], [1.0])

# Safety checks in case user overwritten --srcdir
AC_CONFIG_SRCDIR([test_package.cpp])


# Store the auxiliary build tools (e.g., install-sh, config.sub, config.guess)
# in this dir (build-aux)
AC_CONFIG_AUX_DIR([build-aux])

# Init automake, and specify this program use relaxed structures.
# i.e. this program doesn't follow the gnu coding standards, and doesn't have
# ChangeLog, COPYING, AUTHORS, INSTALL, README etc. files.
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

# Test includes of extra including directories using conan
AUTOMAKE_TEST_PACKAGE_PREREQ([1.0])
AUTOMAKE_TEST_PACKAGE_HELLO([argument1], [argument2], [...], [last argument])

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
