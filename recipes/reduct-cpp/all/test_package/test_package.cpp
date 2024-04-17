#include "reduct/client.h"

#include <iostream>

using reduct::IBucket;
using reduct::IClient;

// Don't call this function. we should avoid hitting the network layer.
extern
void dummy() {
    auto client = IClient::Build("http://127.0.0.1:8383");

    // Get information about the server
    auto [info, err] = client->GetInfo();
    if (err) {
        std::cerr << "Error: " << err << '\n';
    }
}

int main() {

    return 0;
}
