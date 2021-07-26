#include <iostream>
#include <string>
#include <fakeit.hpp>

using namespace fakeit;

struct SomeInterface
{
    virtual int foo(int) = 0;
    virtual int bar(std::string) = 0;
};

int main(int, char**)
{
    Mock<SomeInterface> mock;

    When(Method(mock,foo)).Return(0);
    SomeInterface& i = mock.get();

    // Production code
    i.foo(1);
    // Verify method mock.foo was invoked.
    Verify(Method(mock,foo));
    // Verify method mock.foo was invoked with specific arguments.
    Verify(Method(mock,foo).Using(1));

    std::cout << "Success !" << std::endl;

    return 0;
}
