#include <stdio.h>
#include <librdkafka/rdkafka.h>

int main(int argc, char const *argv[]) {
  rd_kafka_conf_t *conf = rd_kafka_conf_new();

  printf("\n");
  printf("----------------->Tests are done.<---------------------\n");
  printf("Using version (from C lib) %s\n", rd_kafka_version_str());
  printf("///////////////////////////////////////////////////////\n");
  return 0;
}
