#include <iostream>

#include <testcontainers/version.hpp>

// Consumer smoke test, run by `conan create` with no Docker daemon around.
// dependency_report() calls into libarchive/OpenSSL at runtime, proving the
// static library's transitive link lines — CCI wants exactly this and no
// more: test the packaged artifacts, not the library's API.
int main() {
    std::cout << testcontainers::dependency_report();
    return testcontainers::version().empty() ? 1 : 0;
}
