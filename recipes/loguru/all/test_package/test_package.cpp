// Partially taken from: https://github.com/emilk/loguru/tree/master/loguru_example

#include <iostream>
#include <loguru.hpp>
#include <chrono>
#include <thread>

inline void sleep_ms(int ms)
{
    VLOG_F(2, "Sleeping for %d ms", ms);
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

inline void complex_calculation()
{
    LOG_SCOPE_F(INFO, "complex_calculation");
    LOG_F(INFO, "Starting time machine...");
    LOG_F(WARNING, "The flux capacitor is not getting enough power!");
    LOG_F(INFO, "Lighting strike!");
    VLOG_F(1, "Found 1.21 gigawatts...");
}

int main(int argc, char *argv[])
{
    loguru::init(argc, argv);
    LOG_F(INFO, "Hello from main.cpp!");
    complex_calculation();
    LOG_F(INFO, "main function about to end!");
}
