#include <iostream>
#include <Corrade/version.h>

#ifdef WITH_UTILITY
  #include <Corrade/Utility/Debug.h>
#endif


int main() {
  std::cout << "Corrade " << CORRADE_VERSION_YEAR << "." << CORRADE_VERSION_MONTH << std::endl;
  #ifdef WITH_UTILITY
    Corrade::Utility::Debug{} << "Success";
  #endif
}
