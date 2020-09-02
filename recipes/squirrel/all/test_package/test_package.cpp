#include <stdarg.h>
#include <stdio.h>

#include <squirrel.h>
#include <sqstdio.h>
#include <sqstdaux.h>

#ifdef SQUNICODE
#define scvprintf vfwprintf
#else
#define scvprintf vfprintf
#endif


void printfunc(HSQUIRRELVM v,const SQChar *s,...)
{
    va_list vl;
    va_start(vl, s);
    scvprintf(stdout, s, vl);
    va_end(vl);
}

void errorfunc(HSQUIRRELVM v,const SQChar *s,...)
{
    va_list vl;
    va_start(vl, s);
    scvprintf(stderr, s, vl);
    va_end(vl);
}

int main()
{
    HSQUIRRELVM v;
    v = sq_open(1024);

    sqstd_seterrorhandlers(v);

    sq_setprintfunc(v, printfunc, errorfunc);

    sq_pushroottable(v);

    sqstd_register_iolib(v);

    sq_pop(v, 1);
    sq_close(v);

    return 0;
}
