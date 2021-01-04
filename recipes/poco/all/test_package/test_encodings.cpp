#include "Poco/TextEncoding.h"

#include <iostream>

using namespace Poco;

int main() {
    auto encoding = TextEncoding::find("utf8");
    const unsigned char utf8_bytes[] = {0xf0, 0x9f, 0x92, 0x90, 0x00};
    const int expected_unicode = 0x1f490;
    int unicode = encoding->convert(utf8_bytes);

    if (unicode != expected_unicode) {
        std::cerr << "Wrong unicode point!\n"
                  << "Expected " << expected_unicode << ", got " << unicode << "\n";
        return 1;
    }
    std::cout << "decoded unicode point correct!\n";

    return 0;
}
