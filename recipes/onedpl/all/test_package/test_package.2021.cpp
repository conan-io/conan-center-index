#include <vector>
#include <oneapi/dpl/execution>
#include <oneapi/dpl/algorithm>

int main()
{
    std::vector<int> data(10000000);
    auto policy = oneapi::dpl::execution::par_unseq;
    std::fill_n(policy, data.begin(), data.size(), -1);

    return 0;
}
