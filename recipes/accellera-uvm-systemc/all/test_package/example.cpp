#include "uvmsc/base/uvm_version.h"
#include "systemc"
#include <iostream>

using namespace uvm;

// Required for linking with SystemC
int sc_main(int, char*[])
{
  return 0;
}

int main(int, char*[])
{
  std::cout << "uvm-systemc version " << uvm_revision_string() << " loaded successfully.";
  return 0;
}
