#include <iostream>

#include "raylib.h"

int main(void) {
  Vector3 center = {0, 0, 0};
  float r = 1.0;
  if (CheckCollisionSpheres(center, r, center, r)) {
    std::cout << "unit sphere collides with itself!" << std::endl;
  }
  return 0;
}
