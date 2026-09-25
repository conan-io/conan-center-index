#include <kalshi/kalshi.hpp>

#include <iostream>

int main() {
	const kalshi::Result<kalshi::Timestamp> time = kalshi::parse_timestamp("2026-09-25T00:00:00Z");
	std::cout << "kalshi-cpp " << kalshi::VERSION << (time ? " ok" : " failed") << '\n';
	return time ? 0 : 1;
}
