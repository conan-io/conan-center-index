#include <iostream>
#include <cmath>

#include "mapbox/eternal.hpp"

struct Color {
    constexpr inline Color() {
    }
    constexpr inline Color(unsigned char r_, unsigned char g_, unsigned char b_, float a_)
        : r(r_), g(g_), b(b_), a(a_ > 1 ? 1 : a_ < 0 ? 0 : a_) {
    }
    unsigned char r = 0, g = 0, b = 0;
    float a = 1.0f;

    constexpr bool operator==(const Color& rhs) const {
        return r == rhs.r && g == rhs.g && b == rhs.b &&
               (a >= rhs.a ? a - rhs.a : rhs.a - a) < std::numeric_limits<float>::epsilon();
    }
};

MAPBOX_ETERNAL_CONSTEXPR const auto multi_colors = mapbox::eternal::map<mapbox::eternal::string, Color>({
    { "red", { 255, 0, 0, 1 } },
    { "yellow", { 255, 255, 0, 1 } },
    { "white", { 255, 255, 255, 1 } }, // comes before yellow!
    { "yellow", { 255, 220, 0, 1 } },  // a darker yellow
});

int main(void) {
    static_assert(!multi_colors.unique(), "multi_colors are not unique");
    static_assert(multi_colors.find("yellow") != multi_colors.end(), "colors contains yellow");
    static_assert(multi_colors.find("yellow")->second == Color(255, 255, 0, 1), "yellow returns the correct color");
    static_assert((++multi_colors.find("yellow"))->second == Color(255, 220, 0, 1), "yellow returns the correct color");
    static_assert(multi_colors.equal_range("white").first == multi_colors.find("white"), "white range returns the correct begin");
    static_assert(multi_colors.equal_range("white").second == multi_colors.find("yellow"), "white range end is the next color");
    static_assert(multi_colors.equal_range("yellow").first == multi_colors.find("yellow"), "yellow range returns the correct begin");
    static_assert(multi_colors.equal_range("yellow").second == multi_colors.end(), "yellow range end returns end");
    static_assert(multi_colors.count("yellow") == 2, "has 2 yellows");

    return EXIT_SUCCESS;
}
