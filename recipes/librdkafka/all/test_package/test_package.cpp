#include <iostream>
#include <librdkafka/rdkafka.h>

int main(int argc, char const *argv[]) {
  rd_kafka_conf_t *conf = rd_kafka_conf_new();
  std::cout << std::endl
            << "----------------->Tests are done.<---------------------" << std::endl
	    << "Using version " << rd_kafka_version_str() << std::endl
            << "///////////////////////////////////////////////////////" << std::endl;
  return 0;
}
