#include <id3tag.h>

#include <stdio.h>

int main()
{
    printf("id3tag version: %s\n", id3_version);
    printf("id3tag copyright: %s\n", id3_copyright);
    printf("id3tag author: %s\n", id3_author);
    printf("id3tag build: %s\n", id3_build);

    struct id3_tag tag;
    id3_tag_version(&tag);

    return 0;
}
