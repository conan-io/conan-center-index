#include <ConstexprCore/perfect_hash.h>

#include <cstdio>
#include <cstdlib>

using namespace ConstexprCore;

static constexpr auto methods = make_perfect_map<kv<"GET", 0>, kv<"POST", 1>, kv<"PUT", 2>>();

int main() {
    const auto put = methods.lookup("PUT");
    std::printf("perfect_hash %s: PUT -> %d\n", perfect_hash_version, put ? *put : -1);
    return put == 2 && !methods.lookup("BREW") ? EXIT_SUCCESS : EXIT_FAILURE;
}
