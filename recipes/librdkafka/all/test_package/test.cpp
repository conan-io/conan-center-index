#include <iostream>
#include <librdkafka/rdkafka.h>

int main(int argc, char const *argv[]) {
  rd_kafka_conf_t *conf = rd_kafka_conf_new();
  std::cout << std::endl
            << "----------------->Tests are done for now.<---------------------" << std::endl
            << "///////////////////////////////////////////////////////////////" << std::endl;
  return 0;
}
