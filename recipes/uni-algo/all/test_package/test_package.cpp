// This code was cited from https://github.com/uni-algo/uni-algo/tree/v0.1.0#convert-module
#include "uni_algo/all.h"

int main() {
    // Lenient conversion (cannot fail) "\xD800" is unpaired high surrogate in
    // UTF-16
    {
#ifdef UNI_ALGO_NAMESPACE_UNI
        std::string str8 = uni::utf16to8(u"Te\xD800st");
#else
        std::string str8 = una::utf16to8(u"Te\xD800st");
#endif
        assert(str8 == "Te\xEF\xBF\xBDst"); // "\xEF\xBF\xBD" is replacement
                                            // character U+FFFD in UTF-8
    }

    // Strict conversion
    {
#ifdef UNI_ALGO_NAMESPACE_UNI
        uni::error error;
        std::string str8 = uni::strict::utf16to8(u"Te\xD800st", error);
#else
        una::error error;
        std::string str8 = una::strict::utf16to8(u"Te\xD800st", error);
#endif
        assert(str8.empty() && error && error.pos() == 2);
    }

    return 0;
}
