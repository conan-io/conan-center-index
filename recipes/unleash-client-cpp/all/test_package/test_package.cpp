#include <unleash/unleashclient.h>

#include <iostream>

int main() {
    unleash::UnleashClient unleashClient = unleash::UnleashClient::create("production", "urlMock");
    std::cout << unleashClient << std::endl;
    unleashClient.initializeClient();
    unleashClient.isEnabled("feature.toogle");
    return 0;
}
