#include <stdio.h>
#include <string.h>
#include "unrar/rar.hpp"

int
main(int argc, char ** argv)
{
#ifdef _UNIX
    setlocale(LC_ALL,"");
#endif

    InitConsole();
    ErrHandler.SetSignalHandlers(true);
    return 0;
}
