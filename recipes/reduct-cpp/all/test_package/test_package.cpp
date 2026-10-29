#include "reduct/client.h"

#include <iostream>

using reduct::IBucket;
using reduct::IClient;

/* It's a constructor with no network calls, so it's safe to use in test */
int main() {
    auto client = IClient::Build("");
    return EXIT_SUCCESS;
}
