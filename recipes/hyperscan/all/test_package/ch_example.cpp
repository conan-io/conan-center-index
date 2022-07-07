#include <cstdio>
#include <cstring>
#include "hs/ch.h"

struct test_context
{
    const char* ref = nullptr;
    int match_cnt = 0;
    int capture_cnt = 0;
};

static int match_handler(unsigned int id, unsigned long long from, unsigned long long to, unsigned int flags, unsigned int size, const ch_capture_t *captured, void *context)
{
    std::printf("Found match %u from %llu to %llu\n", id, from, to);
    if(size==2)
    {
        std::printf("Found capture from %llu to %llu\n", captured[1].from, captured[1].to);
        if(captured[1].from == 6 && captured[1].to == 9)
        {
            ((test_context*)context)->capture_cnt++;
        }
    }
    ((test_context*)context)->match_cnt++;
    ++(*((int*)context));
    return 0;
}

int main(int argc, char **argv)
{
    std::printf("%s\n", ch_version());

    int retval = 0;
    test_context ctx;
    ctx.ref = "123abcdefghijkl";
    ch_compile_error_t *err = nullptr;
    ch_database_t *db = nullptr;
    ch_scratch_t *scratch = nullptr;

    if (ch_compile("abc(\\w+)ghi", 0, CH_MODE_GROUPS, nullptr, &db, &err) != CH_SUCCESS) {
        std::printf("Failed to compile database\n");
        std::printf("%s\n", err->message);
        retval = 1;
        goto ret;
    }

    if (ch_alloc_scratch(db, &scratch) != CH_SUCCESS) {
        std::printf("Failed to allocate scratch space\n");
        retval = 1;
        goto ret;
    }

    if (ch_scan(db, ctx.ref, std::strlen(ctx.ref), 0, scratch, &match_handler, nullptr, &ctx) != CH_SUCCESS) {
        std::printf("Scan failed.\n");
        retval = 1;
        goto ret;
    }

    if (ctx.match_cnt != 1 || ctx.capture_cnt != 1) {
        retval = 1;
        goto ret;
    }

ret:
    ch_free_compile_error(err);
    ch_free_database(db);
    ch_free_scratch(scratch);

    return retval;
}
