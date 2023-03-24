#include <cstdlib>
#include <iostream>
#include <PcapPlusPlusVersion.h>

int main() {
    std::cout << "PCAP++ VERSION: " << pcpp::getPcapPlusPlusVersionFull() << std::endl;
    return EXIT_SUCCESS;
}
