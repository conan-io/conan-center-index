#include <fplus/fplus.hpp>

#include <iostream>
#include <list>
#include <string>

int main()
{
    std::list<std::string> things = {"same old", "same old"};
    if (fplus::all_the_same(things)) {
        std::cout << "All things being equal." << std::endl;
    }
    return 0;
}
