#include <cstdlib>
#include <iostream>
#include <tao/json/internal/sha256.hpp>


int main() {
   tao::json::internal::sha256 value;
   value.feed("Conan.io");
   std::cout << "SHA256: " << value.get() << std::endl;

   return EXIT_SUCCESS;
}
