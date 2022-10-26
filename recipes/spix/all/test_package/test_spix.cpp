#include <cstdlib>
#include <iostream>

#include "Spix/QtQmlBot.h"

class MyTests : public spix::TestServer
{
protected:
    void executeTest() override
    {
    }
};

int main(void)
{
    spix::QtQmlBot bot;
    MyTests tests;
    bot.runTestServer(tests);

    return EXIT_SUCCESS;
}
