#include <iostream>
#include <thread>

#include "libfork/task.hpp"
#include "libfork/schedule/busy_pool.hpp"


/// Short-hand for a task that uses the busy_pool scheduler.
template <typename T>
using pool_task = lf::basic_task<T, lf::busy_pool::context>;

/// Compute the n'th fibonacci number
auto fib(int n) -> pool_task<int> { 

  if (n < 2) {
    co_return n;
  }

  auto a = co_await fib(n - 1).fork(); // Spawn a child task.
  auto b = co_await fib(n - 2);        // Execute inline.

  co_await lf::join();                 // Wait for children.

  co_return *a + b;                    // Use * to dereference a future.
}


auto main() -> int {
    lf::busy_pool pool;

    int fib_10 = pool.schedule(fib(10));

    std::cout << "Test package output fib10 = " << fib_10 << std::endl;
}
