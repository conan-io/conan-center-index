#include <tinyutf8/tinyutf8.h>

#include <algorithm>
#include <iostream>

int main() {
    tiny_utf8::string str = u8"!🌍 olleH";
    std::for_each(str.rbegin(), str.rend(), [](char32_t codepoint) {
        std::cout << codepoint;
    });

    return 0;
}
