#include <fastrtps/participant/Participant.h>
#include <fastrtps/Domain.h>

int main()
{
	eprosima::fastrtps::Participant *participant{};
    eprosima::fastrtps::Domain::removeParticipant(participant);
}
