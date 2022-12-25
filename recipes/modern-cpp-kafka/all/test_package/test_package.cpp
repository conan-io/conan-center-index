#include "kafka/Utility.h"

#include <iostream>

int main()
{
  std::cout << "librdkafka version: " << kafka::utility::getLibRdKafkaVersion() << std::endl;
}
