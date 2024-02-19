#include <hayai/hayai.hpp>

#include <chrono>
#include <thread>

BENCHMARK(SomeSleep, Sleep1ms, 5, 10) {
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
}
