#include <vector>
#include <iostream>
#include <cppcoro/generator.hpp>
#include <cppcoro/async_mutex.hpp>
#include <cppcoro/task.hpp>

cppcoro::generator<int> intYielder() {
    co_yield 0;
    co_yield 1;
}

// Compile only test, uses code from the library instead of solely in headers
cppcoro::async_mutex mutex;
cppcoro::task<> testMutex() {
    cppcoro::async_mutex_lock lock = co_await mutex.scoped_lock_async();
}

int main() {
    std::vector<int> v;
    for (int n : intYielder()) {
        std::cout << "yielded " << n << '\n';
        v.push_back(n);
    }

    bool success = v[0] == 0 && v[1] == 1;
    if (success) {
        std::cout << "success";
        return 0;
    } else {
        return 1;
    }
}
