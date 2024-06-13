#include <hazelcast/client/hazelcast_client.h>
#include <iostream>

int main() {
    std::cout << "Hazelcast version: " << hazelcast::client::version();
    return EXIT_SUCCESS;
}
