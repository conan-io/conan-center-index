#include <uvgrtp/lib.hh>
#include <iostream>
#include <string>

int main() {
    uvgrtp::context ctx;

    // Get the CNAME (Canonical Name) generated for this context
    std::string cname = ctx.get_cname();
    std::cout << "Generated CNAME: " << cname << std::endl;

    // Check if crypto is enabled in this build of uvgRTP
    bool crypto_enabled = ctx.crypto_enabled();
    std::cout << "Crypto enabled: " << (crypto_enabled ? "Yes" : "No") << std::endl;

    return 0;
}
