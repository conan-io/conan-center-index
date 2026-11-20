#include <atomic>
#include <cstddef>
#include <cstdlib>
#include <iostream>

#include "citor/hints.h"
#include "citor/thread_pool.h"

int main() {
    citor::ThreadPool pool(2);
    std::atomic<std::size_t> seen{0};
    pool.parallelFor<citor::HintsDefaults>(
        std::size_t{0}, std::size_t{1000}, [&](std::size_t lo, std::size_t hi) {
            seen.fetch_add(hi - lo, std::memory_order_relaxed);
        });
    std::cout << "citor parallelFor visited " << seen.load() << " items\n";
    return seen.load() == 1000 ? EXIT_SUCCESS : EXIT_FAILURE;
}
