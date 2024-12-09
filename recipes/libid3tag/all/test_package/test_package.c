#include <id3tag.h>

#include <stdio.h>

int main()
{
    printf("id3tag version: %s\n", ID3_VERSION);
    printf("id3tag author: %s\n", ID3_AUTHOR);
    #ifndef CCI_SKIP_GLOBALS
    // Ensure extern variables also work.
    // This is disabled for shared due to Window
    // WINDOWS_EXPORT_ALL_SYMBOLS still needs __declspec usage
    // for global data symbols as per CMake docs
    // but upstream does not use it
    printf("id3tag build: %s\n", id3_build);
    #endif

    struct id3_tag tag;
    id3_tag_version(&tag);

    printf("id3tag default tag version: %d\n", tag.version);
    return 0;
}
