#include <fbow/fbow.h>
#include <fbow/cpu.h>
#include <iostream>

int main() {
    auto features = fbow::cpu();
    features.detect_host();
    std::cout << "CPU Vendor String: " << fbow::cpu::get_vendor_string() << '\n';
    std::cout << "64-bit = " << features.OS_x64 << '\n';
}
