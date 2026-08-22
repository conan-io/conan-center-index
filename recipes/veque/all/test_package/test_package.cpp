#include <iostream>
#include "veque.hpp"


int main()
{
    veque::veque<float> v;
    v.push_front(1.f);

    auto r = v.back();
    v.pop_back();

    std::cout << "veque::veque works!";
    return 0;
}
