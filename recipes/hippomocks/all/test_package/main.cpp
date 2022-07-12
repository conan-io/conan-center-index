#include <HippoMocks/hippomocks.h>

struct Foo {
public:
	virtual ~Foo() {}
	virtual void f() {}
	virtual void g() = 0;
};

int main()
{
    MockRepository mocks;
    Foo *iamock = mocks.Mock<Foo>();
    mocks.ExpectCall(iamock, Foo::f);
    mocks.ExpectCall(iamock, Foo::g);
    mocks.ExpectCall(iamock, Foo::f);
    iamock->f();
    iamock->g();
    iamock->f();
}
