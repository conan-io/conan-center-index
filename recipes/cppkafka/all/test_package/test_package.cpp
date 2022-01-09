#include <cppkafka/cppkafka.h>
#include <iostream>
#include <string>

using namespace std;
using namespace cppkafka;

int main() {
    // Create the config

	/*
    try {
	    Configuration kafkaConfig;
	    kafkaConfig = {
            {"metadata.broker.list", "68.169.103.40:9092"},
            {"group.id",             "xxx"},
            //{"auto.offset.reset", "earliest"},
            // Disable auto commit
            {"enable.auto.commit",   false}
    };
	        // Create the producer
    Producer producer(kafkaConfig);

    // Produce a message!
    string message = "hey there!";
    producer.produce(MessageBuilder("my_topic").partition(0).payload(message));
    producer.flush();

    }
    catch (std::exception &e) {
	cout << e.what() << endl;
    }

    */
}
