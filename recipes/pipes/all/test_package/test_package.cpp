// Workaround for pipes not finding size_t
#include <cstddef>

#include <pipes/pipes.hpp>

#include <vector>

int main() {
    auto source = std::vector<int>{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    auto destination = std::vector<int>{};

    source >>= pipes::filter([](int i){ return i % 2 == 0; })
        >>= pipes::transform([](int i){ return i * 2; })
        >>= pipes::push_back(destination);

    auto expected = std::vector<int>{0, 4, 8, 12, 16};
    bool success = destination == expected;

    return success ? 0 : 1;
}
