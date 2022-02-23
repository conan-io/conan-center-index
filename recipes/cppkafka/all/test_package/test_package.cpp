#include "cppkafka/cppkafka.h"
#include <iostream>
#include <string>

using namespace cppkafka;

int main() {
    try {
        // Create the config
        Configuration kafkaConfig = {
            {"metadata.broker.list", "127.0.0.1:9092"},
            {"group.id", "xxx"},
            {"auto.offset.reset", "earliest"},
            {"enable.auto.commit", false}
        };

        // Create the producer
        Producer producer(kafkaConfig);

        // Produce a message!
        std::string message = "hey there!";
        producer.produce(MessageBuilder("my_topic").partition(0).payload(message));
        producer.flush();
    } catch (std::exception& e) {
        std::cout << e.what() << std::endl;
    }

    return 0;
}
