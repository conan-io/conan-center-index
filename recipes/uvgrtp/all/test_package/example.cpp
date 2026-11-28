#include <uvgrtp/lib.hh>
#include <iostream>

int main() {
    std::cout << "uvgRTP version: " << uvgrtp::get_version_cstr() << std::endl;
    uvgrtp::context ctx;

    // Check if crypto is enabled in this build of uvgRTP
    bool crypto_enabled = ctx.crypto_enabled();
    std::cout << "Crypto enabled: " << (crypto_enabled ? "Yes" : "No") << std::endl;

    return crypto_enabled == bool(UVGRTP_EXPECT_CRYPTO) ? 0 : 1;
}
