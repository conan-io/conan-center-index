#include <D3D12MemAlloc.h>
#include <iostream>
int main() {
  // A simple test to check the ability to link with the library
  D3D12MA::ALLOCATOR_DESC allocatorDesc = {};
  D3D12MA::Allocator* allocator;
  HRESULT hr = D3D12MA::CreateAllocator(&allocatorDesc, &allocator);
  std::cout << "Alloactor result: " << hr << std::endl;
  return 0;
}
