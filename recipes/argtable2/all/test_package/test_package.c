/*********************************************************************
Example source code for using the argtable2 library to implement:

    echo [-neE] [--help] [--version] [STRING]...

This file is part of the argtable2 library.
Copyright (C) 1998-2001,2003-2011 Stewart Heitmann
sheitmann@users.sourceforge.net

The argtable2 library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
USA.
**********************************************************************/

#include "argtable2.h"

/* Here we only approximate the echo functionality */
void mymain(int n, int e, int E, const char** strings, int nstrings)
    {
    int j;

    printf("option -n = %s\n", ((n)?"YES":"NO"));
    printf("option -e = %s\n", ((e)?"YES":"NO"));
    printf("option -E = %s\n", ((E)?"YES":"NO"));
    for (j=0; j<nstrings; j++)
        printf("%s ", strings[j]);
    printf("\n");
    }


int main(int argc, char **argv)
    {
    /* Define the allowable command line options, collecting them in argtable[] */
    struct arg_lit *n     = arg_lit0("n", NULL,         "do not output the trailing newline");
    struct arg_lit *e     = arg_lit0("e", NULL,         "enable interpretation of the backslash-escaped characters listed below");
    struct arg_lit *E     = arg_lit0("E", NULL,         "disable interpretation of those sequences in <string>s");
    struct arg_lit *help  = arg_lit0(NULL,"help",       "print this help and exit");
    struct arg_lit *vers  = arg_lit0(NULL,"version",    "print version information and exit");
    struct arg_str *strs  = arg_strn(NULL,NULL,"STRING",0,argc+2,NULL);
    struct arg_end *end   = arg_end(20);
    void* argtable[] = {n,e,E,help,vers,strs,end};
    const char* progname = "echo";
    int exitcode=0;
    int nerrors;

    /* verify the argtable[] entries were allocated sucessfully */
    if (arg_nullcheck(argtable) != 0)
        {
        /* NULL entries were detected, some allocations must have failed */
        printf("%s: insufficient memory\n",progname);
        exitcode=1;
        goto exit;
        }

    /* Parse the command line as defined by argtable[] */
    nerrors = arg_parse(argc,argv,argtable);

    /* special case: '--help' takes precedence over error reporting */
    if (help->count > 0)
        {
        printf("Usage: %s", progname);
        arg_print_syntax(stdout,argtable,"\n");
        printf("Echo the STRINGs to standard output.\n\n");
        arg_print_glossary(stdout,argtable,"  %-10s %s\n");
        printf("\nWithout -E, the following sequences are recognized and interpolated:\n\n"
               "  \\NNN   the character whose ASCII code is NNN (octal)\n"
               "  \\\\     backslash\n"
               "  \\a     alert (BEL)\n"
               "  \\b     backspace\n"
               "  \\c     suppress trailing newline\n"
               "  \\f     form feed\n"
               "  \\n     new line\n"
               "  \\r     carriage return\n"
               "  \\t     horizontal tab\n"
               "  \\v     vertical tab\n\n"
               "Report bugs to <foo@bar>.\n");
        exitcode=0;
        goto exit;
        }

    /* special case: '--version' takes precedence error reporting */
    if (vers->count > 0)
        {
        printf("'%s' example program for the \"argtable\" command line argument parser.\n",progname);
        printf("September 2003, Stewart Heitmann\n");
        exitcode=0;
        goto exit;
        }

    /* If the parser returned any errors then display them and exit */
    if (nerrors > 0)
        {
        /* Display the error details contained in the arg_end struct.*/
        arg_print_errors(stdout,end,progname);
        printf("Try '%s --help' for more information.\n",progname);
        exitcode=1;
        goto exit;
        }

    /* Command line parsing is complete, do the main processing */
    mymain(n->count, e->count, E->count, strs->sval, strs->count);

    exit:
    /* deallocate each non-null entry in argtable[] */
    arg_freetable(argtable,sizeof(argtable)/sizeof(argtable[0]));

    return exitcode;
    }
