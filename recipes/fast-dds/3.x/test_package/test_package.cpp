#include <fastdds/dds/domain/DomainParticipant.hpp>
#include <fastdds/dds/domain/DomainParticipantFactory.hpp>
#include <fastdds/dds/publisher/Publisher.hpp>
#include <fastdds/dds/publisher/DataWriter.hpp>
#include <iostream>

#include "HelloWorld.hpp"
#include "HelloWorldPubSubTypes.hpp"

using namespace eprosima::fastdds::dds;

int main() {
  // Define msg to send
  HelloWorld hello;
  hello.index(0);
  hello.message("HelloWorld");

  auto factory = DomainParticipantFactory::get_instance();
  auto *participant = factory->create_participant_with_default_profile(
      nullptr, StatusMask::none());

  if (participant == nullptr) {
    return 1;
  }

  TypeSupport helloWorldPubSubType{new HelloWorldPubSubType()};

  helloWorldPubSubType.register_type(participant);

  PublisherQos publisherQos = PUBLISHER_QOS_DEFAULT;
  participant->get_default_publisher_qos(publisherQos);
  auto *publisher =
      participant->create_publisher(publisherQos, nullptr, StatusMask::none());

  if (publisher == nullptr) {
    return 1;
  }

  TopicQos topicQos = TOPIC_QOS_DEFAULT;
  participant->get_default_topic_qos(topicQos);
  auto* topic = participant->create_topic("HelloWorldTopic", helloWorldPubSubType.get_type_name(), topicQos);

  if (topic == nullptr) {
    return 1;
  }

  DataWriterQos writerQos = DATAWRITER_QOS_DEFAULT;
  writerQos.history().depth = 5;
  publisher->get_default_datawriter_qos(writerQos);
  DataWriter* writer = publisher->create_datawriter(topic, writerQos, nullptr, StatusMask::all());

  if (writer == nullptr) {
    return 1;
  }

  writer->write(&hello);

  participant->delete_contained_entities();

  DomainParticipantFactory::get_instance()->delete_participant(participant);

  return 0;
}
