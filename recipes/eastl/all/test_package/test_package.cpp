#include <EASTL/algorithm.h>
#include <vector>

int main()
{
    std::vector<int> vec;
    eastl::max_element(vec.begin(), vec.end());
    return 0;
}
