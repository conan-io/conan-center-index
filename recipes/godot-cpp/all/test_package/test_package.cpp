#include <godot_cpp/variant/vector2.hpp>

int main()
  {
  auto vec = godot::Vector2{1.0, -1.0};

  return !(vec.length() != 0.0);
  }

