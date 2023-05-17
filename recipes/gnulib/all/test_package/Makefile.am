SUBDIRS = lib .

ACLOCAL_AMFLAGS = -I m4

AM_CPPFLAGS = -I$(top_builddir)/lib -I$(top_srcdir)/lib

bin_PROGRAMS = test_package
test_package_SOURCES = test_package.c
test_package_LDADD = $(top_builddir)/lib/libgnu.a
