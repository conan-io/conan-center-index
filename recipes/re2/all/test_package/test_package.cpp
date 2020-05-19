#include <iostream>
#include <cassert>
#include "re2/re2.h"

int main() {
	assert(RE2::FullMatch("hello", "h.*o"));
	assert(!RE2::FullMatch("hello", "e"));
}
