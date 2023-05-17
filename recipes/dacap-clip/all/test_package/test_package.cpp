#include <iostream>
#include "clip.h"

int main() {
  clip::set_text("Hello World");

  std::string value;
  clip::get_text(value);
  std::cout << value << std::endl;

  return 0;
}
