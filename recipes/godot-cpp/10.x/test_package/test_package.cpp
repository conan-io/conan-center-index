// Exercises both include trees shipped by the package: the static headers
// (include/godot_cpp/...) and the generated bindings (gdextension_interface.h,
// include/godot_cpp/classes/..., include/godot_cpp/variant/...).
#include <gdextension_interface.h>
#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/vector2.hpp>

int main() {
    godot::Vector2 v{1.0, -1.0};
    return (v.x == 1.0 && v.y == -1.0) ? 0 : 1;
}
