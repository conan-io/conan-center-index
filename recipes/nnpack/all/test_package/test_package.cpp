#include <iostream>
#include "nnpack.h"


int main(void) {
   auto result = nnp_initialize();
   std::cout << "NNPACK initialization result: " << result << std::endl;
   nnp_deinitialize();
   return 0;
}
