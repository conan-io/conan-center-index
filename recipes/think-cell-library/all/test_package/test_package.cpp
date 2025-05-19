#include "tc/range/meta.h"
#include "tc/range/filter_adaptor.h"
#include "tc/string/format.h"
#include "tc/string/make_c_str.h"

#include <vector>
#include <cstdio>
#include <cstdlib>

namespace {

template <typename... Args>
void print(Args&&... args) noexcept {
	std::printf("%s", tc::implicit_cast<char const*>(tc::make_c_str<char>(std::forward<Args>(args)...)));
}

int main(void) {
	std::vector<int> v = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20};

	tc::for_each(
		tc::filter(v, [](const int& n){ return (n%2==0);}),
		[&](auto const& n) {
			print(tc::as_dec(n), ", ");
		}
	);
	print("\n");
	return EXIT_SUCCESS;
}
