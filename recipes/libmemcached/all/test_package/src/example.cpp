#include <iostream>
#include <libmemcached-1.0/memcached.h>

int main() {
    std::cout << memcached_lib_version() << '\n';
    return 0;
}
