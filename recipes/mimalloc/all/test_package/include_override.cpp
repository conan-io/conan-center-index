#ifdef _WIN32
#include <mimalloc-new-delete.h>
#else
#include <mimalloc.h>
#endif

#include <iostream>
#include <memory>

int main() {
    auto *data = new int(1024);
    delete data;

    std::cout << "mimalloc version " << mi_version() << "\n";
    return 0;
}
