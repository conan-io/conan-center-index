/* test_package.f -- translated by f2c (version 20160102).
   You must link the resulting object file with libf2c:
	on Microsoft Windows system, link with libf2c.lib;
	on Linux or Unix systems, link with .../path/to/libf2c.a -lm
	or, if you install libf2c.a in a standard place, with -lf2c -lm
	-- in that order, at the end of the command line, as in
		cc *.o -lf2c -lm
	Source for libf2c is in /netlib/f2c/libf2c.zip, e.g.,

		http://www.netlib.org/f2c/libf2c.zip
*/

#include "f2c.h"

/* Table of constant values */

static integer c__9 = 9;
static integer c__1 = 1;

/* Main program */ int MAIN__(void)
{
    /* Builtin functions */
    integer s_wsle(cilist *), do_lio(integer *, integer *, char *, ftnlen),
	    e_wsle(void);
    /* Subroutine */ int s_stop(char *, ftnlen);

    /* Fortran I/O blocks */
    static cilist io___1 = { 0, 6, 0, 0, 0 };


    s_wsle(&io___1);
    do_lio(&c__9, &c__1, "libf2c: Hello, World!", (ftnlen)21);
    e_wsle();
    s_stop("", (ftnlen)0);
    return 0;
} /* MAIN__ */

/* Main program alias */ int hello_ () { MAIN__ (); return 0; }
