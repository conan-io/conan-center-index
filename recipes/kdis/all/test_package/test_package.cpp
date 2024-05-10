#include <iostream>

#include "KDIS/PDU/Entity_Info_Interaction/Entity_State_PDU.h"

int main() {
  KDIS::PDU::Entity_State_PDU pdu;
  auto force = pdu.GetForceID();
  return EXIT_SUCCESS;
}
