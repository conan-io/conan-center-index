#include <cstdlib>
#include <iostream>
#include "async_simple/coro/Lazy.h"
#include "async_simple/coro/SyncAwait.h"
using namespace async_simple::coro;

Lazy<int> foo() {
    co_return 1;
}

int main(void) {
    std::cout << "test async_simple" << std::endl;
    auto lazy_task = foo();
    auto ret = syncAwait(lazy_task);
    if (ret != 1) {
        std::cout << "ERROR: " << ret << std::endl;
        std::cout << EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
