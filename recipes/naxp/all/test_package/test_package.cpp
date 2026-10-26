#include <naxp/naxp.hpp>

#include <cstdint>
#include <cstdio>

// Compiled as C, to prove that naxp.h is usable from C.
extern "C" std::uint64_t encode_with_c_interface(const char *pattern, const char *text);

int main()
{
	const auto postcode = logmu::naxp::parse(R"(\A\A?\9\X? \s \9\A\A)");
	const std::uint64_t value = postcode.encode("M1 1AA");
	const std::uint64_t value_from_c = encode_with_c_interface("\\A\\A?\\9\\X? \\s \\9\\A\\A", "M1 1AA");

	std::printf("naxp: %llu encodes to %llu and back to %s; the C interface gives %llu\n",
		static_cast<unsigned long long>(postcode.max_encoded_value()),
		static_cast<unsigned long long>(value),
		postcode.decode(value).c_str(),
		static_cast<unsigned long long>(value_from_c));

	return value == 810639597u && value_from_c == value ? 0 : 1;
}
