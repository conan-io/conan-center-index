# @configure_input@

bin_PROGRAMS = test_package
lib_LTLIBRARIES = libtestlib.la

test_package_SOURCES = test_package.c
test_package_LDADD = libtestlib.la

libtestlib_la_SOURCES = lib.c
libtestlib_la_LDFLAGS = -no-undefined -export-symbols "$(srcdir)/libtestlib.sym"
include_HEADERS = lib.h

ACLOCAL_AMFLAGS = -I m4
