#include <mad.h>

#include <stdio.h>

int main()
{
    printf("mad version: %s\n", mad_version);
    printf("mad copyright: %s\n", mad_copyright);
    printf("mad author: %s\n", mad_author);
    printf("mad build: %s\n", mad_build);
    return 0;
}
