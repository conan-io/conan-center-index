#include <accessor/accessor.hpp>
#include <iostream>

class Test
{
  int mFooBar {1};
};

using TestFooBar = accessor::MemberWrapper<Test, int>;
template class accessor::MakeProxy<TestFooBar, &Test::mFooBar>;

int main()
{
    Test t;
    (void)accessor::accessMember<TestFooBar>(t);

    std::cout << "cpp-member-accessor test_package PASSED!" << std::endl;
    return 0;
}
