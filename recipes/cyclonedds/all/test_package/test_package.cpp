
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <thread>

#include "dds/dds.h"
#include "Message.h"

int main() {
  dds_entity_t participant;
  dds_entity_t topic;

  /* Create a Participant. */
  participant = dds_create_participant (DDS_DOMAIN_DEFAULT, NULL, NULL);
  if (participant < 0)
    DDS_FATAL("dds_create_participant: %s\n", dds_strretcode(-participant));

  conan_cyclonedds_Message msg;
  msg.payload._length = 0;

  return EXIT_SUCCESS;
}
