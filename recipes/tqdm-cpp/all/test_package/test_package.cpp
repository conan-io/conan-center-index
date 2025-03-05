#include <tqdm.hpp>

#include <vector>
#include <chrono>
#include <thread>

int main()
{
    using namespace std::chrono_literals;
    auto delay = 5ms;
    std::vector<int> A(50, 0);
    for (int a : tq::tqdm(A)) {
        std::this_thread::sleep_for(delay);
    }
    return 0;
}
