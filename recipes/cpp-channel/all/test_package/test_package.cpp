#include <iostream>

#include "msd/channel.hpp"

int main()
{
    msd::channel<int> ch{10};

    int in{};

    in = 1;
    ch << in;

    in = 2;
    ch << in;

    in = 3;
    ch << in;

    for (auto out : ch) {
        std::cout << out << '\n';

        if (ch.empty()) {
            break;
        }
    }
}
