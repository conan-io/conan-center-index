#include <archive.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("libarchive version: %s\n", archive_version_string());
    printf("libarchive details: %s\n", archive_version_details());
    return 0;
}
