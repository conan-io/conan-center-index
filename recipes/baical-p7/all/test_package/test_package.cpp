#include <cstdlib>
#include <iostream>

#include "P7_Trace.h"

// Test to validate Conan package generated

int main(int /*argc*/, const char * /*argv*/ []) {

  IP7_Client        *l_pClient    = NULL;
  //create P7 client object
  l_pClient = P7_Create_Client(TM("/P7.Pool=32768"));
  if (l_pClient == NULL) {
    std::cout << "Client is null.\n";
    return EXIT_FAILURE;
  }
    std::cout << "Created client successfully.\n";
  if (l_pClient)
  {
      l_pClient->Release();
      l_pClient = NULL;
  }
  return EXIT_SUCCESS;
}
