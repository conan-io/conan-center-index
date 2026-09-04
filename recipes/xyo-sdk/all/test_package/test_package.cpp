#include <xyo/xyo_client.hpp>
#include <iostream>
#include <utility>

int main() {
    xyo::ClientConfig config("test_api_key");
    xyo::XyoClient client(std::move(config));
    std::cout << "XYO SDK initialized successfully in Conan test package\n";
    return 0;
}
