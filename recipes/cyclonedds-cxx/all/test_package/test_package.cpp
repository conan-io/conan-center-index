
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>

#include "dds/dds.hpp"
#include "Message.hpp"

int main() {
  dds_entity_t participant;
  dds_entity_t topic;

  /* Create a Participant. */
  dds::domain::DomainParticipant domain_(0);

  /* Create a Message. */
  conan::cyclonedds::Message message;
  std::vector<unsigned char> payload;
  message.payload(std::move(payload));

  return EXIT_SUCCESS;
}
