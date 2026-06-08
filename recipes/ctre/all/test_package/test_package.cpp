#include <ctre.hpp>
#include <string_view>
#include <iostream>

static constexpr auto pattern = ctll::fixed_string{ "[a-z]+([0-9]+)" };

// Example from Readme
constexpr std::optional<std::string_view> extract_number(std::string_view s) noexcept {
    if (auto m = ctre::match<pattern>(s)) {
        return m.get<1>().to_view();
    } else {
        return std::nullopt;
    }
}

int main() {
	using namespace std::literals;
    constexpr std::string_view text = "abc123";
	
	static_assert(extract_number(text) == "123"sv);

	std::cout << "ctre test package successful\n";
}

