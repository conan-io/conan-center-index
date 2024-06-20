#include <cstdlib>
#include <iostream>

#include "libfork.hpp"

namespace {
    constexpr auto hello_async_world = [](auto /* self */) -> lf::task<int> {
        std::cout << "Hello, async world!" << std::endl;
        co_return 0;
    };
}

auto main() -> int {
    try {
        return lf::sync_wait(lf::lazy_pool{}, hello_async_world);
    } catch (std::exception const &e) {
        std::cerr << "Caught exception: " << e.what() << std::endl;
        return EXIT_FAILURE;
    } catch (...) {
        std::cerr << "Caught unknown exception." << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
