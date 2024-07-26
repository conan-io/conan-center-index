#include <iostream>
#include <cassert>
#include "icurve/copypp.hh"

class A {
public:
    int id;
    std::string name;
    bool sex;

public:
    A() = default;
    A(int id, std::string name, bool sex) : id(id), name(name), sex(sex) {}
};

class B {
public:
    int id;
    std::string name;
    bool sex;

public:
    B() = default;
    B(int id, std::string name, bool sex) : id(id), name(name), sex(sex) {}
};

COPYPP_FIELDS_NON_INTRUSIVE(B, A, id, name, sex)

int main(void) {
    A a(1, "curve", true);
    B b;
    icurve::copy(b, a);
    assert(a.id == b.id);
    assert(a.name == b.name);
    assert(a.sex == b.sex);
    std::cout << "copypp ok" << std::endl;
    return EXIT_SUCCESS;
}
