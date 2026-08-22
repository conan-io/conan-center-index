#include <cerrno>
#include <cstdlib>
#include <cstdio>

#include <sdbus-c++/Error.h>

int main() {
    std::puts("Create error object");
    auto error = sdbus::createError(ENOMEM, "test message");
    if (error.getName() != "org.freedesktop.DBus.Error.NoMemory") {
        std::puts("Failed");
        return EXIT_FAILURE;
    }
    std::puts("Success");
}
