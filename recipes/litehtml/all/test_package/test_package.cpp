#include "litehtml/litehtml.h"
#include "litehtml/tstring_view.h"

#include <iostream>

int main() {    
    constexpr size_t offset = 5;
    constexpr size_t length = 10;

    litehtml::tstring string = _t("the quick brown fox jumps over the lazy dog");
    litehtml::tstring_view view(string.data() + offset, length);

    for (auto c : view) {
        std::cout << c << std::endl;
    }
  return 0;
}
