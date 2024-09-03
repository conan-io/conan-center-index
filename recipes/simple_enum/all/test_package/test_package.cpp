#include <simple_enum/simple_enum.hpp>

int main() {
    enum struct enum_bounded  {  v1 = 1,  v2,  v3,  first = v1,  last = v3  };
    static_assert(simple_enum::enum_name(enum_bounded::v2) == "v2");

    return 0;
}
