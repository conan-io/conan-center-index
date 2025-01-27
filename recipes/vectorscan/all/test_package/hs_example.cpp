#include <cstdio>
#include "hs.h"

int main(int argc, char **argv) {
    hs_compile_error_t* err = nullptr;
    hs_database_t* db = nullptr;

    const auto result = hs_compile("abc", HS_FLAG_SOM_LEFTMOST, HS_MODE_BLOCK, nullptr, &db, &err);
    if (result != HS_SUCCESS) {
        std::printf("Failed to compile database\n");
        std::printf("%s\n", err->message);
        return 1;
    }

    return 0;
}
