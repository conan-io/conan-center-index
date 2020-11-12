#include <args/parser.hpp>
#include <cstdio>
#include <numeric>
#include <vector>

template <typename Pred>
unsigned accumulate(std::vector<unsigned> const& integers, Pred pred) {
    return std::accumulate(integers.begin(), integers.end(), 0u, pred);
}

int main(int argc, char* argv[]) {
    std::vector<unsigned> integers{};
    bool is_sum{false};

    args::null_translator tr{};
    args::parser parser{"Process some integers.",
        args::from_main(argc, argv), &tr};
    parser.set<std::true_type>(is_sum, "sum")
        .opt()
        .help("sum the integers (default: find the max)");
    parser.arg(integers)
        .meta("N")
        .help("an integer for the accumulator");

    parser.parse();

    auto const result =
        is_sum ? accumulate(integers, [](auto a, auto b) { return a + b; })
               : accumulate(integers,
                            [](auto a, auto b) { return std::max(a, b); });
    printf("%u\n", result);
}
