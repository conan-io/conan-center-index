#include "nonstd/jthread.hpp"
#include <iostream>

using nonstd::jthread;

int main()
{
    int product = 0;
    const int six = 6;
    const int seven = 7;

    {
        nonstd::jthread thr{[&](int x, int y){ product = x * y; }, six, seven };

        // automatically join thread here, making sure it has executed:
    }

    return !( product == six * seven );
}
