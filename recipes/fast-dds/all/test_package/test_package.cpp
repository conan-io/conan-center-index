#ifdef FASTDDS_VERSION_3
#include <fastdds/dds/domain/DomainParticipant.hpp>
#else
#include <fastrtps/Domain.h>
#include <fastrtps/participant/Participant.h>
#endif


int main() {
#ifdef FASTDDS_VERSION_3
  dds::domain::DomainParticipant *participant{};
#else
  eprosima::fastrtps::Participant *participant{};
  eprosima::fastrtps::Domain::removeParticipant(participant);
#endif
}
