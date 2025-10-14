#include <zeroipc/memory.h>
#include <zeroipc/array.h>
#include <zeroipc/queue.h>
#include <zeroipc/future.h>
#include <iostream>

int main() {
    std::cout << "ZeroIPC Conan Package Test" << std::endl;
    
    try {
        // Basic functionality test
        zeroipc::Memory mem("/conan_test", 1024*1024);
        zeroipc::Array<double> arr(mem, "test_array", 5);
        
        // Write and read test
        for (int i = 0; i < 5; ++i) {
            arr[i] = i * 1.5;
        }
        
        // Verify
        for (int i = 0; i < 5; ++i) {
            if (arr[i] != i * 1.5) {
                std::cerr << "Array test failed at index " << i << std::endl;
                return 1;
            }
        }
        
        // Queue test
        zeroipc::Queue<int> queue(mem, "test_queue", 3);
        queue.push(10);
        queue.push(20);
        
        auto val = queue.pop();
        if (!val || *val != 10) {
            std::cerr << "Queue test failed" << std::endl;
            return 1;
        }
        
        // Future test
        zeroipc::Future<float> future(mem, "test_future");
        future.set_value(3.14f);
        
        if (future.get() != 3.14f) {
            std::cerr << "Future test failed" << std::endl;
            return 1;
        }
        
        std::cout << "ZeroIPC Conan package test: SUCCESS!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Test failed with exception: " << e.what() << std::endl;
        return 1;
    }
}