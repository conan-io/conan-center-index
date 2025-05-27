#include <qc-hash.hpp>
#include <cassert>
#include <iostream>
#include <string>

int main()
{
    qc::hash::RawMap<unsigned int, std::string> m{};

    m.insert({42, "foo"});
    m.insert({7, "bar"});

    assert(m.contains(42));
    assert(m.at(42) == "foo");
    assert(m.contains(7));
    assert(m.at(7) == "bar");

    std::cout << "OK" << std::endl;
    return 0;
}