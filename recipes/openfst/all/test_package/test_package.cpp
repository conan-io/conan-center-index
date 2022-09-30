#include <fst/fstlib.h>
#include <iostream>

int main() {
  fst::StdVectorFst v_fst;
  std::cout << v_fst.NumStates() << std::endl;
  return 0;
}
