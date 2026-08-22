#ifdef TEST_DIS7
#include <dis7/EntityStatePdu.h>
#else
#include <dis6/EntityStatePdu.h>
#endif

#include <iostream>

int main() {
  DIS::EntityStatePdu pdu1, pdu2;

  DIS::DataStream ds(DIS::BIG);
  pdu1.marshal(ds);
  pdu2.unmarshal(ds);

  std::cout << "Success\n";
  return EXIT_SUCCESS;
}
