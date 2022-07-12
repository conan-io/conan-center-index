#include <bpstd/optional.hpp>
#include <iostream>

int main() {
    bpstd::optional<int> optional{};
    std::cout << std::boolalpha;
    std::cout << "default optional: " << optional.has_value() << std::endl;
    optional.emplace(42);
    std::cout << "set optional: " << optional.has_value() << ", " <<  optional.value() << std::endl;
    optional.reset();
    std::cout << "reset optional: " << optional.has_value() << std::endl;
    return 0;
}
