#include <tins/tins.h>
#include <tins/data_link_type.h>
#include <tins/tcp_ip/ack_tracker.h>

using namespace Tins;

int main() {
  SnifferConfiguration config;
  config.set_filter("port 80");
  config.set_promisc_mode(true);
  config.set_snap_len(50);
}
