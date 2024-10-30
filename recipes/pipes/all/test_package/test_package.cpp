// Workaround for pipes not finding size_t
#include <cstddef>
#include <cstdlib>
#include <optional>
#include <vector>

#include <pipes/pipes.hpp>


int main() {
    auto source = std::vector<int>{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    auto destination = std::vector<int>{};

    source >>= pipes::filter([](int i){ return i % 2 == 0; })
        >>= pipes::transform([](int i){ return i * 2; })
        >>= pipes::push_back(destination);

    return EXIT_SUCCESS;
}
