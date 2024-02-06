#include <iostream>
#include <string>

#ifndef SCNLIB_V2

#include <scn/scn.h>

int main() {
    std::string word;
    auto result = scn::scan("Hello world", "{}", word);
    std::cout << word << '\n';
    std::cout << result.range_as_string() << '\n';
}

#else

#include <scn/scan.h>

int main() {
    if (auto result = scn::scan<std::string>("Hello world!", "{}")) {
        std::cout << result->value() << '\n';
    } else {
        std::cout << "Couldn't parse a word: " << result.error().msg() << '\n';
    }
}

#endif
