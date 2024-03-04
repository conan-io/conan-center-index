#include <iostream>

#include "dis6/entity_information/EntityStatePdu.h"

int main() {
  dis::EntityStatePdu pdu1, pdu2;

  dis::DataStream ds(dis::kBig);
  pdu1.Marshal(ds);
  pdu2.Unmarshal(ds);

  std::cout << "Success\n";
  return EXIT_SUCCESS;
}
