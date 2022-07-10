#include "daw/utf8/unchecked.h"
#include <iostream>
#include <string>

int main() {
    std::string sample{"あいうえお abcde"};

    auto first = daw::utf8::unchecked::iterator{sample.begin()};
    auto last = daw::utf8::unchecked::iterator{sample.end()};

    int count = 0;
    for (; first != last; ++first) {
        ++count;
    }

    std::cout << count << std::endl;

    return 0;
}
