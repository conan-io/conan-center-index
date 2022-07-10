#include <iostream>
#include <Corrade/Corrade.h>  // Here it is 'nothing'

#ifndef VERSION_2019_10
  #include <Corrade/version.h>
#endif

#ifdef WITH_UTILITY
  #include <Corrade/Utility/Debug.h>
#endif


int main() {
  std::cout << "Test package for Corrade\n";
  
  #ifndef VERSION_2019_10
    std::cout << "Corrade " << CORRADE_VERSION_YEAR << "." << CORRADE_VERSION_MONTH << std::endl;
  #endif

  #ifdef WITH_UTILITY
    Corrade::Utility::Debug{} << "Success";
  #endif
}
