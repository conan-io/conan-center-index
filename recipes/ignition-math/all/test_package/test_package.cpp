/*
 * Copyright (C) 2019 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/
#include <iostream>
#include <ignition/math/Angle.hh>

int main(int argc, char **argv)
{
  // Create an angle.
  ignition::math::Angle a;

  // A default constructed angle should be zero.
  std::cout << "The angle 'a' should be zero: " << a << std::endl;
  a = ignition::math::Angle::Pi;

  // Output the angle in radians and degrees.
  std::cout << "Pi in radians: " << a << std::endl;
  std::cout << "Pi in degrees: " << a.Degree() << std::endl;

  // The Angle class overloads the +=, and many other, math operators.
  a += ignition::math::Angle::HalfPi;
  std::cout << "Pi + PI/2 in radians: " << a << std::endl;
  std::cout << "Normalized to the range -Pi and Pi: "
    << a.Normalized() << std::endl;
}
