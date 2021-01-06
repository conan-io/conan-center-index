#include <iostream>

#include "raylib.h"

int main(void) {
  if (CheckCollisionSpheres({0, 0, 0}, 1, {0, 0, 0}, 1)) {
    std::cout << "spheres colliding!" << std::endl;
  }
  return 0;
}
