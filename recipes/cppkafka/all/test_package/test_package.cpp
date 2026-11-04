#include "cppkafka/cppkafka.h"
#include <iostream>
#include <string>

using namespace cppkafka;

int main() {
    try {
        // Create the config
        Configuration kafkaConfig = {
            {"group.id", "xxx"},
            {"auto.offset.reset", "earliest"},
            {"enable.auto.commit", false}
        };


        // Build a topic configuration
        TopicConfiguration topic_config = {
            { "auto.offset.reset", "smallest" }
        };
        kafkaConfig.set_default_topic_configuration(topic_config);
    } catch (std::exception& e) {
        std::cout << e.what() << std::endl;
    }

    return 0;
}
