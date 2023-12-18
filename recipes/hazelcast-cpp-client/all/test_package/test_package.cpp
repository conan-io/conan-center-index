#include <hazelcast/client/hazelcast_client.h>
#include <cstdio>

int main() {
    printf("Hazelcast version: %s", hazelcast::client::version());
    return EXIT_SUCCESS;
}
