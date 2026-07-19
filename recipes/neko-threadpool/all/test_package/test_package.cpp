#include <iostream>
#include <neko/thread/threadPool.hpp>

int main() {
    // Create thread pool (uses hardware thread count by default)
    neko::thread::ThreadPool pool(2);
    
    // Submit simple task
    auto future = pool.submit([]() {
        return 42;
    });
    
    // Get result
    std::cout << "Result: " << future.get() << std::endl;
    
    return EXIT_SUCCESS;
}