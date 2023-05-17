//#define FULL_DISABLE_PROFILER
#include <chrono>
#include <thread>
#include <vector>
#include <iostream>
#include <condition_variable>
#include <cstdlib>
#include <math.h>

#define BUILD_WITH_EASY_PROFILER
#include <easy/profiler.h>
#include <easy/arbitrary_value.h>
#include <easy/reader.h>

int RENDER_STEPS = 300;

//#define SAMPLE_NETWORK_TEST

void localSleep(uint64_t magic=200000)
{
    //PROFILER_BEGIN_FUNCTION_BLOCK_GROUPED(profiler::colors::Blue);
    volatile int i = 0;
    for (; i < magic; ++i);
}

void renderThread(){
    EASY_THREAD("Render");
    uint64_t n = 20;

    for (int i = 0; i < RENDER_STEPS; i++)
    {
        localSleep(1200000);
        n += 20;
        if (n >= 700)
            n = 20;
        //std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
}

//////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[])
{
  #ifndef SAMPLE_NETWORK_TEST
    EASY_PROFILER_ENABLE;
  #endif
    EASY_MAIN_THREAD;
    profiler::startListen();

    renderThread();

    std::cout << "SUCCESS" << std::endl;
    
    return 0;
}
