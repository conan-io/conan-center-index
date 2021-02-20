#include <vector>
#include <utility>
#include <fn.hpp>

namespace fn = rangeless::fn;
using fn::operators::operator%;   // arg % fn   equivalent to fn(std::forward<Arg>(arg))
using fn::operators::operator%=;  // arg %= fn; equivalent to arg = fn( std::move(arg));

int main() {
    auto values = std::vector<int>{0,1,2,3,4,5,6,7,8,9,10};
    values = std::move(values)
        % fn::where([](auto&& _) { return _ % 2 == 0; })
        % fn::transform([] (auto&& _) { return _ * 3; });
    
    auto expected = std::vector<int>{0,6,12,18,24,30};
    bool success = values == expected;

    return success ? 0 : 1;
}
