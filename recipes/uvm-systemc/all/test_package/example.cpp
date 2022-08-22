#include "uvmsc/base/uvm_version.h"
#include <iostream>

using namespace uvm;

int main(int, char*[])
{
  std::cout << "uvm-systemc version " << uvm_revision_string() << " loaded successfully.";

  return 0;
}