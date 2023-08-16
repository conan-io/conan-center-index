#include <string>
#include <iostream>

#include "zpp_bits.h"

struct person {
    std::string name;
    int age{};
};

int main(void) {
    auto [data, in, out] = zpp::bits::data_in_out();

    out(person{"Person1", 25}, person{"Person2", 35});

    person p1, p2;

    in(p1, p2);

    std::cout << p1.name << " : " << p1.age << "\n";
    std::cout << p2.name << " : " << p2.age << "\n";

    return 0;
}
