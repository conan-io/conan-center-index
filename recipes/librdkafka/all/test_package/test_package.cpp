#include <iostream>
#include <librdkafka/rdkafka.h>
#include <librdkafka/rdkafkacpp.h>

int main(int argc, char const *argv[]) {
  rd_kafka_conf_t *conf = rd_kafka_conf_new();
  auto confpp = RdKafka::Conf::create(RdKafka::Conf::CONF_GLOBAL);

  std::cout << std::endl
            << "----------------->Tests are done.<---------------------" << std::endl
            << "Using version (from C lib) " << rd_kafka_version_str() << std::endl
            << "Using version (from C++ lib) " << RdKafka::version() << std::endl
            << "///////////////////////////////////////////////////////" << std::endl;
  return 0;
}
