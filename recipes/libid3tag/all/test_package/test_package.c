#include <id3tag.h>

#include <stdio.h>

int main()
{
    struct id3_tag tag;
    id3_tag_version(&tag);

    printf("id3tag default tag version: %d\n", tag.version);
    return 0;
}
