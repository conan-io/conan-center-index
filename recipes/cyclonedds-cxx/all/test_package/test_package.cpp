#include <vector>
#include "dds/dds.hpp"

int main() {

  dds::domain::DomainParticipant participant(0);
  dds::topic::PublicationBuiltinTopicData topic;
  dds::sub::Subscriber subscriber(participant);

  return 0;
}
