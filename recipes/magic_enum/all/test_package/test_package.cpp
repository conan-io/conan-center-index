#ifdef MAGIC_ENUM_INCLUDE_WITH_FOLDER
#  include <magic_enum/magic_enum.hpp>
#else
#  include <magic_enum.hpp>
#endif
#include <cstdlib>
#include <string>

enum Color { RED = 2, BLUE = 4, GREEN = 8 };

int main(){

    Color color = Color::RED;
    std::string color_name { magic_enum::enum_name(color) };
    return color_name == "RED" ? EXIT_SUCCESS : EXIT_FAILURE ;

}
