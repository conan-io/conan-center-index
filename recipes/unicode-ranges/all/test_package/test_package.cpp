#include "unicode_ranges_all.hpp"

#include <string_view>

using namespace unicode_ranges;

int main()
{
    auto text = utf8_string::from_bytes(std::string_view{ "Gr\xC3\xBC\xC3\x9F" });
    if (!text)
        return 1;
    return text->to_utf16().char_count() == text->char_count() ? 0 : 2;
}
