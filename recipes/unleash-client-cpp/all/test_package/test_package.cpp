#include <cassert>
#include <ios>
#include <iostream>

#include <unleash/unleashclient.h>

int main() {
    unleash::UnleashClient unleashClient = unleash::UnleashClient::create("production", "https://www.apple.com/%");
    std::cout << "feature.toggle - is enabled: " << std::boolalpha << unleashClient.isEnabled("feature.toogle") << '\n';
    return 0;
}
