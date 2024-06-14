#include <stdlib.h>
#include "dds/dds.h"
#include "test_message.h"
#include "idl/string.h"

int main() {
  dds_entity_t participant;
  participant = dds_create_participant (DDS_DOMAIN_DEFAULT, NULL, NULL);
  if (participant < 0)
    DDS_FATAL("dds_create_participant: %s\n", dds_strretcode(-participant));

  conan_test_message msg;
  msg.payload._length = 0;
  unsigned int val = idl_isalnum('1');

  if(!val)
    return EXIT_FAILURE;

  return EXIT_SUCCESS;
}
