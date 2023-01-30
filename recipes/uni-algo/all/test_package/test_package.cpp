// This code was cited from https://github.com/uni-algo/uni-algo/tree/v0.1.0#convert-module
#include "uni_algo/all.h"

int main() {
    // Lenient conversion (cannot fail) "\xD800" is unpaired high surrogate in
    // UTF-16
    {
        std::string str8 = uni::utf16to8(u"Te\xD800st");
        assert(str8 == "Te\xEF\xBF\xBDst"); // "\xEF\xBF\xBD" is replacement
                                            // character U+FFFD in UTF-8
    }

    // Strict conversion
    {
        uni::error error;
        std::string str8 = uni::strict::utf16to8(u"Te\xD800st", error);
        assert(str8.empty() && error && error.pos() == 2);
    }

    return 0;
}
