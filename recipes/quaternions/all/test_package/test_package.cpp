#include <quaternion.h>
#include <quaternion_io.h>

#include <iostream>

int main () {
  quaternion::Quaternion<float> q1(1.0f, 0.0f, 0.0f, 0.0f);
  quaternion::Quaternion<float> q2(0.0f, 1.0f, 0.0f, 0.0f);
  quaternion::Quaternion<float> q3(0.0f, 0.0f, 1.0f, 0.0f);
  auto q4 = q1 * q2 * q3;
  std::cout << q4 << std::endl;
  return 0;
}
