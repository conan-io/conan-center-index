#include <iostream>
#include <libp2p/multi/multiaddress.hpp>

int main() {
  auto addr = libp2p::multi::Multiaddress::create("/ip4/192.168.0.1/tcp/8080");
  std::cout << "address: " << addr.value().getStringAddress() << std::endl;
  return 0;
}
