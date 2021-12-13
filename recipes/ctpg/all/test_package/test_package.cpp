#include "ctpg.hpp"
#include <iostream>

constexpr ctpg::nterm<int> list("list");
constexpr char number_pattern[] = "[1-9][0-9]*";
constexpr ctpg::regex_term<number_pattern> number("number");

int to_int(std::string_view sv) {
    int i = 0;
    for (auto c : sv) {
        i = i * 10 + (c - '0');
    }
    return i;
}

constexpr ctpg::parser p(
    list,
    terms(',', number),
    nterms(list),
    rules(
        list(number) >= to_int,
        list(list, ',', number) >= [](int sum, char, const auto& n){ return sum + to_int(n); }
    )
);

int main(int argc, char* argv[]) {
    auto res = p.parse(ctpg::buffers::string_buffer("10, 20, 30"), std::cerr);
    bool success = res.has_value();
    if (success)
        std::cout << res.value() << std::endl;
    return success ? 0 : -1;
}
