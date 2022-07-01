#include <indirect_value.h>

using namespace isocpp_p1950;

int main()
{
    indirect_value<int> result{new int(EXIT_SUCCESS)};
    return *result;
}
