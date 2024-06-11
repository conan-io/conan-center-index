#include <cstdlib>
#include <iostream>
#include "pcapplusplus/PcapPlusPlusVersion.h"

int main() {
    std::cout << "PCAP++ VERSION: " << pcpp::getPcapPlusPlusVersionFull() << std::endl;
    return EXIT_SUCCESS;
}
