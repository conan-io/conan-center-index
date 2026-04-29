#include <stdexec/execution.hpp>

#include <cstdlib>

int main() {
    auto work = stdexec::starts_on(stdexec::get_parallel_scheduler(), stdexec::just(42));
    auto [value] = stdexec::sync_wait(std::move(work)).value();
    return value == 42 ? EXIT_SUCCESS : EXIT_FAILURE;
}
