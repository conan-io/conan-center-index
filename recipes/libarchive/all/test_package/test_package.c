#include <archive.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("libarchive version: %s\n", archive_version_string());
    printf("libarchive details: %s\n", archive_version_details());

    // Further test correct linkage against upstreams
    struct archive * a = archive_read_new();
    archive_read_support_filter_all(a);
    archive_read_free(a);

    return 0;
}
