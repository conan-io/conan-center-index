#include <cstdlib>
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>

#include "Spix/QtQmlBot.h"

std::mutex m;
std::condition_variable cv;

class MyTests : public spix::TestServer
{
protected:
    void executeTest() override { cv.notify_one(); }
};

int main(void)
{
    spix::QtQmlBot bot;
    MyTests tests;
    bot.runTestServer(tests);

    // wait for the test to begin before exiting main,
    // destroying the server before the test is launched
    std::unique_lock lk(m);
    cv.wait(lk);

    return EXIT_SUCCESS;
}
