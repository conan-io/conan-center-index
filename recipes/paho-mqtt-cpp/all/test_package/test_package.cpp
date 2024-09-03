#include <iostream>
#include "mqtt/message.h"


int main() {
    mqtt::message msg("hello", "Hello there", 11, 1, true);
    std::cout << "MQTT topic: " << msg.get_topic() << std::endl;

    return 0;
}
