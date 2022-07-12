#include <cstdio>
#include <cstring>
#include <memory>
#include <tuple>
#include "hs/ch.h"

struct context_t
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
            ((context_t*)context)->capture_cnt++;
        }
    }
    ((context_t*)context)->match_cnt++;
    ++(*((int*)context));
    return 0;
}


static std::tuple<std::shared_ptr<ch_database_t>, std::shared_ptr<ch_compile_error_t>, ch_error_t> compile(const char* pattern)
{
    ch_compile_error_t* err = nullptr;
    ch_database_t* db = nullptr;

    const auto result = ch_compile(pattern, 0, CH_MODE_GROUPS, nullptr, &db, &err);

    return std::tuple<std::shared_ptr<ch_database_t>, std::shared_ptr<ch_compile_error_t>, ch_error_t>(
        std::shared_ptr<ch_database_t>(db, ch_free_database),
        std::shared_ptr<ch_compile_error_t>(err, ch_free_compile_error),
        result
    );
}

static std::pair<std::shared_ptr<ch_scratch_t>, ch_error_t> alloc_scratch(ch_database_t& db)
{
    ch_scratch_t* scratch = nullptr;

    const auto result = ch_alloc_scratch(&db, &scratch);

    return std::pair<std::shared_ptr<ch_scratch_t>, ch_error_t>(
        std::shared_ptr<ch_scratch_t>(scratch, ch_free_scratch),
        result
    );
}

static ch_error_t scan(ch_database_t& db, ch_scratch_t& scratch, const char* data, ch_match_event_handler handler, void* context)
{
    const auto len = std::strlen(data);
    return ch_scan(&db, data, len, 0, &scratch, match_handler, nullptr, context);
}

int main(int argc, char **argv)
{
    printf("%s\n", ch_version());

    context_t ctx;
    ctx.ref = "123abcdefghijkl";
    std::shared_ptr<ch_compile_error_t> err;
    std::shared_ptr<ch_database_t> db;

    ch_error_t result;

    std::tie(db, err, result) = compile("abc(\\w+)ghi");

    if (result != CH_SUCCESS) {
        std::printf("Failed to compile database\n");
        std::printf("%s\n", err->message);
    }
    else
    {
        std::shared_ptr<ch_scratch_t> scratch;

        std::tie(scratch, result) = alloc_scratch(*db);
        if (result != CH_SUCCESS) {
            std::printf("Failed to allocate scratch space\n");
        }
        else
        {
            if(scan(*db, *scratch, ctx.ref, &match_handler, &ctx) == CH_SUCCESS)
            {
                if (ctx.match_cnt == 1 && ctx.capture_cnt == 1) {
                    return 0;
                }
            }
        }
    }

    return -1;
}
