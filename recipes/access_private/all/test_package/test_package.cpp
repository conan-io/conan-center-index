#include <access_private.hpp>

class A {
    int m_i = 3;
};

ACCESS_PRIVATE_FIELD(A, int, m_i)

int main()
{
    const A a;
    const int val = access_private::m_i(a);
    if (val == 3) {
        return 0;
    }
    return -1;
}
