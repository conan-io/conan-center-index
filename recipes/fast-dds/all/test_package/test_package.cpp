#include <iostream>
#include <fastrtps/participant/Participant.h>
#include <fastrtps/attributes/ParticipantAttributes.h>
#include <fastrtps/attributes/PublisherAttributes.h>
#include <fastrtps/publisher/Publisher.h>
#include <fastrtps/Domain.h>

#include "msg/HelloWorld.h"
#include "msg/HelloWorldPubSubTypes.h"

int main()
{
    // Define msg to send 
    HelloWorld hello;
    hello.index(0);
    hello.message("HelloWorld");

	eprosima::fastrtps::Participant *participant;
	eprosima::fastrtps::Publisher *publisher;

    eprosima::fastrtps::ParticipantAttributes PParam;
    PParam.rtps.setName("Participant_pub");
    participant = eprosima::fastrtps::Domain::createParticipant(PParam);

    if (participant == nullptr)
    {
        return 1;
    }

    HelloWorldPubSubType type;

    eprosima::fastrtps::Domain::registerType(participant, &type);

    //CREATE THE PUBLISHER
    eprosima::fastrtps::PublisherAttributes Wparam;
    Wparam.topic.topicKind = eprosima::fastrtps::rtps::TopicKind_t::NO_KEY;
    Wparam.topic.topicDataType = "HelloWorld";
    Wparam.topic.topicName = "HelloWorldTopic";
    Wparam.topic.historyQos.kind = eprosima::fastrtps::KEEP_LAST_HISTORY_QOS;
    Wparam.topic.historyQos.depth = 30;
    Wparam.topic.resourceLimitsQos.max_samples = 50;
    Wparam.topic.resourceLimitsQos.allocated_samples = 20;
    Wparam.times.heartbeatPeriod.seconds = 2;
    Wparam.times.heartbeatPeriod.nanosec = 200 * 1000 * 1000;
    publisher = eprosima::fastrtps::Domain::createPublisher(participant, Wparam);
    if (publisher == nullptr)
    {
        return 1;
    }

    publisher->write((void*)&hello);

    eprosima::fastrtps::Domain::removeParticipant(participant);

    return 0;
}
