#include <cstdio>
#include "hs/hs.h"

static int match_handler(unsigned int id, unsigned long long from, unsigned long long to, unsigned int flags, void *context)
{
    std::printf("Found match %u from %llu to %llu\n", id, from, to);
    ++(*((int*)context));
    return 0;
}

int main(int argc, char **argv)
{
    std::printf("%s\n", hs_version());

    int retval = 0;
    int match_cnt = 0;
    hs_compile_error_t *err = nullptr;
    hs_database_t *db = nullptr;
    hs_scratch_t *scratch = nullptr;

    if (hs_compile("abc", HS_FLAG_SOM_LEFTMOST, HS_MODE_BLOCK, NULL, &db, &err) != HS_SUCCESS) {
        std::printf("Failed to compile database\n");
        std::printf("%s\n", err->message);
        retval = 1;
        goto ret;
    }

    if (hs_alloc_scratch(db, &scratch) != HS_SUCCESS) {
        std::printf("Failed to allocate scratch space\n");
        retval = 1;
        goto ret;
    }

    if (hs_scan(db, "123abcdef", 9, 0, scratch, &match_handler, &match_cnt) != HS_SUCCESS) {
        std::printf("Scan failed.\n");
        retval = 1;
        goto ret;
    }

    if (match_cnt != 1) {
        retval = 1;
        goto ret;
    }

ret:
    hs_free_compile_error(err);
    hs_free_database(db);
    hs_free_scratch(scratch);

    return 0;
}
