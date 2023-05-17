#include <trantor/net/EventLoopThread.h>

#include <iostream>
#include <atomic>
#include <future>

#ifndef _WIN32
#include <unistd.h>
#endif

int main() {
    std::atomic<bool> flag(false);
    {
        trantor::EventLoopThread thr;
        thr.getLoop()->runOnQuit([&]() { flag = true; });
        thr.run();
        thr.getLoop()->quit();
    }

    if (flag == false) {
        std::cerr << "Test failed\n";
    }
    else {
        std::cout << "Success\n";
    }

    return 0;
}
