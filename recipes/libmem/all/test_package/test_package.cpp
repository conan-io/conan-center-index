#include <libmem/libmem.hpp>
#include <iostream>
#include <vector>
#include <optional>

using namespace libmem;

int main() {
    std::optional<Thread> currentThread = GetThread();
    if (currentThread.has_value()) {
        std::cout << "libmem C++ API test: Successfully got current thread" << std::endl;
    } else {
        std::cout << "libmem C++ API test: Failed to get current thread" << std::endl;
    }
    std::optional<std::vector<Thread>> threads = EnumThreads();
    if (threads.has_value()) {
        std::cout << "libmem C++ API test: Successfully enumerated threads, count: " 
                    << threads->size() << std::endl;
    } else {
        std::cout << "libmem C++ API test: Failed to enumerate threads" << std::endl;
    }
    return 0;
}
