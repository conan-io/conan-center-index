#include <neko/log/nlog.hpp>


int main(void) {
    using namespace neko;
    log::setCurrentThreadName("Main Thread");
    log::setLevel(log::Level::Debug);
    log::info("This is an info message.");

    return EXIT_SUCCESS;
}