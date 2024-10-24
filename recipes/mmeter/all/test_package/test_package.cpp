#include "MMeter.h"
#include <iomanip>
#include <iostream>
#include <thread>

int calcInt(int ctr)
{
    MMETER_FUNC_PROFILER;

    int val = 0;
    for (int i = 0; i <= ctr; i++)
        val += i;

    return val;
}

int calcFloat(int ctr)
{
    MMETER_FUNC_PROFILER;

    float val = 0;
    for (int i = 0; i <= ctr; i++)
        val += i;

    return val;
}

void test()
{
    MMETER_FUNC_PROFILER;
    calcInt(50000000);
    calcFloat(50000000);
}

int main()
{
    std::thread t1([]() {
        MMETER_SCOPE_PROFILER("main function subthread");
        test();
        test();
    });
    t1.join();

    std::cout << std::fixed << std::setprecision(6) << MMeter::getGlobalTreePtr()->totalsByDurationStr() << std::endl;
    std::cout << *MMeter::getGlobalTreePtr() << std::endl;
    MMeter::getGlobalTreePtr()->outputBranchPercentagesToOStream(std::cout);
}
