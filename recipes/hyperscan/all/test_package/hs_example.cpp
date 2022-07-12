#include <cstdio>
#include <cstring>
#include <memory>
#include <tuple>
#include "hs/hs.h"

static int match_handler(unsigned int id, unsigned long long from, unsigned long long to, unsigned int flags, void *context)
{
    std::printf("Found match %u from %llu to %llu\n", id, from, to);
    ++(*((int*)context));
    return 0;
}

static std::tuple<std::shared_ptr<hs_database_t>, std::shared_ptr<hs_compile_error_t>, hs_error_t> compile(const char* pattern)
{
    hs_compile_error_t* err = nullptr;
    hs_database_t* db = nullptr;

    const auto result = hs_compile(pattern, HS_FLAG_SOM_LEFTMOST, HS_MODE_BLOCK, nullptr, &db, &err);

    return std::tuple<std::shared_ptr<hs_database_t>, std::shared_ptr<hs_compile_error_t>, hs_error_t>(
        std::shared_ptr<hs_database_t>(db, hs_free_database),
        std::shared_ptr<hs_compile_error_t>(err, hs_free_compile_error),
        result
    );
}

static std::pair<std::shared_ptr<hs_scratch_t>, hs_error_t> alloc_scratch(hs_database_t& db)
{
    hs_scratch_t* scratch = nullptr;

    const auto result = hs_alloc_scratch(&db, &scratch);

    return std::pair<std::shared_ptr<hs_scratch_t>, hs_error_t>(
        std::shared_ptr<hs_scratch_t>(scratch, hs_free_scratch),
        result
    );
}

static hs_error_t scan(hs_database_t& db, hs_scratch_t& scratch, const char* data, match_event_handler handler, void* context)
{
    const auto len = std::strlen(data);
    return hs_scan(&db, data, len, 0, &scratch, match_handler, context);
}

int main(int argc, char **argv)
{
    std::printf("%s\n", hs_version());

    int retval = 0;
    int match_cnt = 0;
    
    std::shared_ptr<hs_compile_error_t> err;
    std::shared_ptr<hs_database_t> db;

    hs_error_t result;

    std::tie(db, err, result) = compile("abc");

    if (result != HS_SUCCESS) {
        std::printf("Failed to compile database\n");
        std::printf("%s\n", err->message);
    }
    else
    {
        std::shared_ptr<hs_scratch_t> scratch;

        std::tie(scratch, result) = alloc_scratch(*db);
        if (result != HS_SUCCESS) {
            std::printf("Failed to allocate scratch space\n");
        }
        else
        {
            if(scan(*db, *scratch, "123abcdef", &match_handler, &match_cnt) == HS_SUCCESS)
            {
                if (match_cnt == 1) {
                    return 0;
                }
            }
        }
    }
    return -1;
}
