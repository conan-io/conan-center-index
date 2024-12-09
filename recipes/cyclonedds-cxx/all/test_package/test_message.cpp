#include <vector>
#include "dds/dds.hpp"
#include "Message.hpp"

int main() {
  dds::domain::DomainParticipant domain_(0);

  conan::Message message;
  std::vector<unsigned char> payload;
  message.payload(std::move(payload));
  return 0;
}
