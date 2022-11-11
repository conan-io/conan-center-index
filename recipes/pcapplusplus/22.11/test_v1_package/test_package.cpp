#include <iostream>
#include <IPv4Layer.h>
#include <Packet.h>
#include <PcapFileDevice.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "ERROR: Need at least one argument" << std::endl;
        return 1;
    }

    // open a pcap file for reading
    pcpp::PcapFileReaderDevice reader(argv[1]);
    if (!reader.open()) {
        std::cerr << "ERROR: Error opening the pcap file" << std::endl;
        return 1;
    }

    // read the first (and only) packet from the file
    pcpp::RawPacket rawPacket;
    if (!reader.getNextPacket(rawPacket)) {
        std::cerr << "ERROR: Couldn't read the first packet in the file" << std::endl;
        return 1;
    }

    // parse the raw packet into a parsed packet
    pcpp::Packet parsedPacket(&rawPacket);

    // verify the packet is IPv4
    if (parsedPacket.isPacketOfType(pcpp::IPv4)) {
        // extract source and dest IPs
        pcpp::IPv4Address srcIP = parsedPacket.getLayerOfType<pcpp::IPv4Layer>()->getSrcIPv4Address();
        pcpp::IPv4Address destIP = parsedPacket.getLayerOfType<pcpp::IPv4Layer>()->getDstIPv4Address();

        // print source and dest IPs
        std::cout << "Source IP is '" << srcIP.toString() << "'; Dest IP is '" << destIP.toString() << "'" << std::endl;
    }

    // close the file
    reader.close();

    return 0;
}
