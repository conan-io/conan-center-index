#include <fire-hpp/fire.hpp>
#include <iostream>

int fired_main(int x = fire::arg("-x"), int y = fire::arg("-y")) {
   std::cout << x + y << std::endl;
   return 0;
}

FIRE(fired_main)
