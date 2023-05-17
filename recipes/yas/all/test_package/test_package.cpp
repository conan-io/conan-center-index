/**
 * Example taken from https://github.com/niXman/yas.
 */
#include <cstdlib>

#include <yas/serialize.hpp>
#include <yas/std_types.hpp>

int main() {
    int a = 3;
    int aa{};
    short b = 4;
    short bb{};
    float c = 3.14;
    float cc{};

    constexpr std::size_t flags =
        yas::mem // IO type
        |yas::json; // IO format

    auto buf = yas::save<flags>(
        YAS_OBJECT("myobject", a, b, c)
    );

    yas::load<flags>(buf,
        YAS_OBJECT_NVP("myobject"
            ,("a", aa)
            ,("b", bb)
            ,("c", cc)
        )
    );

    if(a == aa && b == bb && c == cc) {
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}
