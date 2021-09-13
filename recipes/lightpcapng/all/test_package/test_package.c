
#include "light_pcapng_ext.h"

int main(void) {
  const char* outfile = "conan_test.pcapng";
  light_pcapng writer = light_pcapng_open(outfile, "wb");

  light_packet_interface pkt_interface = {0};
  light_packet_header pkt_header = {0};
  uint8_t* pkt_data = NULL;
}

