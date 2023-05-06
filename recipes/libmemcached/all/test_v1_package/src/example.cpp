#include <libmemcached-1.0/memcached.h>
#include <iostream>

int main() {
    std::cout << memcached_lib_version() << '\n';
    return 0;
}
