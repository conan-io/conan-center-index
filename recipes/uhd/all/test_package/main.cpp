#include <uhd/version.hpp>
#include <uhd/device.hpp>
#include <uhd/utils/safe_main.hpp>
#include <iostream>
#include <string>

int UHD_SAFE_MAIN(int argc, char *argv[]) {
    // 1. Get UHD Stack Information
    std::cout << "=======================================" << std::endl;
    std::cout << "UHD Version:     " << uhd::get_version_string() << std::endl;
    std::cout << "UHD ABI Version: " << uhd::get_abi_string() << std::endl;
    std::cout << "=======================================" << std::endl;

    // 2. Scan for Hardware
    std::cout << "Scanning for USRP devices..." << std::endl;
    uhd::device_addr_t hint; // Empty hint finds all
    uhd::device_addrs_t dev_addrs = uhd::device::find(hint);

    if (dev_addrs.size() == 0) {
        std::cout << "No USRP devices found. Check your connections/network." << std::endl;
        return EXIT_FAILURE;
    }

    // 3. Print discovered device info
    for (size_t i = 0; i < dev_addrs.size(); i++) {
        std::cout << "Device [" << i << "]: " << dev_addrs[i].to_pp_string() << std::endl;
    }

    return EXIT_SUCCESS;
}
