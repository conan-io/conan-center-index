#include "BS_thread_pool.hpp"
#include <iostream>

int main()
{
    BS::thread_pool pool;
    std::cout << "Testing thread pool...\n";
    if (pool.get_thread_count() == std::thread::hardware_concurrency())
    {
        std::cout << "SUCCESS: Created " << pool.get_thread_count() << " unique threads!\n";
        return EXIT_SUCCESS;
    }
    else
    {
        std::cout << "ERROR: Failed to create " << pool.get_thread_count() << " unique threads!\n";
        return EXIT_FAILURE;
    }
}
