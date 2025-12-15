#include <D3D12MemAlloc.h>

int main() {
  // A simple test to check the ability to link with the library
  D3D12MA::ALLOCATION_DESC allocDesc = {};
  (void)allocDesc;
  D3D12MA::Allocator *allocator = nullptr;
  (void)allocator;
  return 0;
}
