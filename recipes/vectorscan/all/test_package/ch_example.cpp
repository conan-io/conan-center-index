#include <cstdio>
#include "ch.h"

int main(int argc, char **argv) {
    ch_compile_error_t* err = nullptr;
    ch_database_t* db = nullptr;

    const auto result = ch_compile("abc(\\w+)ghi", 0, CH_MODE_GROUPS, nullptr, &db, &err);
    if (result != CH_SUCCESS) {
        std::printf("Failed to compile database\n");
        std::printf("%s\n", err->message);
        return 1;
    }

    return 0;
}
