#include <termcap.h>

#include <stdio.h>
#include <stdlib.h>

int main()
{
    char buf[2048] = {0};
    char *cl_string, *cm_string;
    int auto_wrap, height, width;

    const char* term = getenv("TERM");
    if (term == NULL) {
        fprintf(stderr, "TERM environment variable not defined\n");
        return 0;
    } else {
        int res = tgetent(buf, term);
        switch(res) {
        case -1: fprintf(stderr, "tgetent: database not found\n"); break;
        case 0: fprintf(stderr, "tgetent: no such entry\n"); break;
        case 1: fprintf(stderr, "tgetent: success\n"); break;
        default: fprintf(stderr, "Unknown tgetent return variable\n"); break;
        }
    }

    cl_string = tgetstr ("cl", NULL);
    cm_string = tgetstr ("cm", NULL);
    auto_wrap = tgetflag ("am");
    height = tgetnum ("li");
    width = tgetnum ("co");

    printf("cl: %s\n", cl_string);
    printf("cm: %s\n", cm_string);
    printf("am: %d\n", auto_wrap);
    printf("li: %d\n", height);
    printf("co: %d\n", width);

    return EXIT_SUCCESS;
}
