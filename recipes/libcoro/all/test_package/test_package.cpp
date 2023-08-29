#include <coro/coro.hpp>
#include <cstdint>
#include <iostream>

int main()
{
    auto task = []() -> coro::task<void> {
        auto fibonacci = []() -> coro::generator<int> {
            int a = 0;
            int b = 1;
            while (true)
            {
                co_yield b;
                int tmp = a;
                a = b;
                b += tmp;
            }
        };

        size_t i = 0;
        for (int x : fibonacci())
        {
            std::cout << x << std::endl;

            if (i++ == 10)
            {
                break;
            }
        }
        co_return;
    };

    coro::sync_wait(task());
    return 0;
}
