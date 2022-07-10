#include <cassert>

#include <unleash/unleashclient.h>

int main() {
    unleash::UnleashClient unleashClient = unleash::UnleashClient::create("production", "https://www.apple.com/%");
    unleashClient.initializeClient();
    return unleashClient.isEnabled("feature.toogle");

}
