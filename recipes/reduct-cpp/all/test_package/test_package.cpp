#include "reduct/client.h"

#include <iostream>

using reduct::IBucket;
using reduct::IClient;

int main() {
    auto client = IClient::Build("http://127.0.0.1:8383");

    // Get information about the server
    auto [info, err] = client->GetInfo();
    if (err) {
        std::cerr << "Error: " << err << '\n';
    }

    return 0;
}
