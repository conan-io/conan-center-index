#include <iostream>
#include <cstring>
#include <memory>
#include <cstdlib>

int main()
{
    size_t size = 1024 * 1024 * 1024; // 1 Gb
    size_t total = 0;
    for (;;) {
        void * ptr = malloc(size);
        if (!ptr)
        {
            std::cerr << "failed to allocate" << std::endl;
            return -1;
        }
        memset(ptr, 1, size);
        total += size;
        std::cout << "allocated : " << total / 1024 / 1024 / 1024 << " Gb" << std::endl;
    }
}

