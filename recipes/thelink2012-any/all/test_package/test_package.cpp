#include <string>

#include "any.hpp"

struct big_type {
    char i_wanna_be_big[256];
    std::string value;

    big_type() :
        value(std::string(300, 'b'))
    {
        i_wanna_be_big[0] = i_wanna_be_big[50] = 'k';
    }
};

int main() {
    linb::any x = 4;
    linb::any y = big_type{};
    linb::any z = 6.5;

    y.clear();

    x = y;

    z = linb::any();

    return 0;
}
