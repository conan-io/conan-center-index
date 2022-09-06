# Must init the autoconf setup
# The first parameter is project name
# second is version number
# third is bug report address
AC_INIT([test_package], [1.0])

# Safety checks in case user overwritten --srcdir
AC_CONFIG_SRCDIR([test_package_c.c])

# Store the auxiliary build tools (e.g., install-sh, config.sub, config.guess)
# in this dir (build-aux)

AC_CONFIG_FILES(Makefile)
AC_CONFIG_HEADER([config.h])

AC_PROG_CC
AC_PROG_CXX

AC_PROG_CC_C_O

AC_MSG_NOTICE("ac_cv_prog_cc_${ac_cc} is $ac_cv_prog_cc_${ac_cc}")
AS_IF([eval test \$ac_cv_prog_cc_${ac_cc}_c_o = "yes"],
 [AC_SUBST([CC_MINUS_O], ["-o"])],[AC_SUBST([CC_MINUS_O], [""])])

AC_OUTPUT
