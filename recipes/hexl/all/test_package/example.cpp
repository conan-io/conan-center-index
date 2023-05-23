#include <cstdint>
#include <iostream>
#include <vector>

#include "hexl/hexl.hpp"

bool CheckEqual(const std::vector<uint64_t>& x,
                const std::vector<uint64_t>& y) {
  if (x.size() != y.size()) {
    std::cout << "Not equal in size\n";
    return false;
  }
  uint64_t N = x.size();
  bool is_match = true;
  for (size_t i = 0; i < N; ++i) {
    if (x[i] != y[i]) {
      std::cout << "Not equal at index " << i << "\n";
      is_match = false;
    }
  }
  return is_match;
}

bool ExampleEltwiseVectorVectorAddMod() {
  std::vector<uint64_t> op1{1, 2, 3, 4, 5, 6, 7, 8};
  std::vector<uint64_t> op2{1, 3, 5, 7, 2, 4, 6, 8};
  uint64_t modulus = 10;
  std::vector<uint64_t> exp_out{2, 5, 8, 1, 7, 0, 3, 6};

  intel::hexl::EltwiseAddMod(op1.data(), op1.data(), op2.data(), op1.size(),
                             modulus);

  return CheckEqual(op1, exp_out);
}

int main() {
  if(ExampleEltwiseVectorVectorAddMod())
  {
      return 0;
  }

  return -1;
}
