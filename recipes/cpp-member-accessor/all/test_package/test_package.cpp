#include <accessor/accessor.hpp>

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
}
