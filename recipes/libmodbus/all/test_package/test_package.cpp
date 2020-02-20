#include <cstdlib>
#include <iostream>

#include "modbus/modbus.h"

int main() {
  
    if(modbus_get_slave(NULL) == -1)
    {
      std::cout << "Modbus package might work" << std::endl;
      return EXIT_SUCCESS;
    }
    else
      return EXIT_FAILURE;
    
}
