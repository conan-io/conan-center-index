#include "effolkronium/random.hpp"

using Random_t = effolkronium::random_local;

int main( ) {
  Random_t localRandom{ }; // Construct on the stack
  
  // access throughout dot
  auto val = localRandom.get(-10, 10);
  
} // Destroy localRandom and free stack memory