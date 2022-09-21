#include <iostream>
#include <librdkafka/rdkafkacpp.h>

int main(int argc, char const *argv[]) {
  RdKafka::Conf* confpp = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);

  std::cout << std::endl
            << "----------------->Tests are done.<---------------------" << std::endl
            << "Using version (from C++ lib) " << RdKafka::version() << std::endl
            << "///////////////////////////////////////////////////////" << std::endl;
  return 0;
}
