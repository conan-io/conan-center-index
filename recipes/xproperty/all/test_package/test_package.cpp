#include <xproperty/xobserved.hpp>

#include <iostream>
#include <stdexcept>

struct Foo: public xp::xobserved<Foo> {
    XPROPERTY(double, Foo, bar);
    XPROPERTY(double, Foo, baz);
};

int main() {
    Foo foo;

    XOBSERVE(foo, bar, [](Foo& f) {
        std::cout << "Observer: New value of bar: " << f.bar << std::endl;
    });

    XVALIDATE(foo, bar, [](Foo&, double& proposal) {
        std::cout << "Validator: Proposal: " << proposal << std::endl;
        if (proposal < 0)
        {
            throw std::runtime_error("Only non-negative values are valid.");
        }
        return proposal;
    });

    foo.bar = 1.0;
    std::cout << foo.bar << std::endl;
    try {
        foo.bar = -1.0;
    } catch (...) {
        std::cout << foo.bar << std::endl;
    }

    return 0;
}
