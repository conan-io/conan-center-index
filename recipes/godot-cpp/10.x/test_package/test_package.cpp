// Exercises both include trees shipped by the package: the static headers and the
// generated bindings. length() is called on purpose, it is compiled into the library
// while Vector2's constructor is constexpr, so the link really uses libgodot-cpp.
#include <gdextension_interface.h>
#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/vector2.hpp>

int main() {
    godot::Vector2 v{3.0f, 4.0f};
    return (v.length() == 5.0f) ? 0 : 1;
}
