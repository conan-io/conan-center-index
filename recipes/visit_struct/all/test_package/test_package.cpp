#include <visit_struct/visit_struct.hpp>

#include <string>
#include <iostream>

struct my_type {
    int         a;
    float       b;
    std::string c;
};

VISITABLE_STRUCT(my_type, a, b, c);

struct debug_printer {
    template <typename T>
    void operator()(const char* name, const T& value) {
        std::cerr << name << ": " << value << std::endl;
    }
};

int main(int argc, char* argv[]) {
    auto val = my_type{1, 2.0f, "three"};

    visit_struct::for_each(val, debug_printer{});

    return 0;
}
