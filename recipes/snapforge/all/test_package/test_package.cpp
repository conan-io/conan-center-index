#include <snapforge/client.hpp>
#include <string>

int main() {
    snapforge::ClientOptions options;
    options.base_url = "https://snapforge.web-tasarimci.com";
    const snapforge::Client client(options);
    return client.base_url() == options.base_url &&
        std::string(snapforge::kVersion) == "0.2.0" ? 0 : 1;
}
