#include <re2/re2.h>

#include <iostream>
#include <cassert>

int main() {
    assert(RE2::FullMatch("hello", "h.*o"));
    assert(!RE2::FullMatch("hello", "e"));
    return 0;
}
