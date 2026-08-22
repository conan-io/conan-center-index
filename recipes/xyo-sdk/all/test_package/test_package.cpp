#include <xyo/xyo_client.hpp>
#include <iostream>

int main() {
    xyo::ClientConfig config("test_api_key");
    xyo::XyoClient client(config);
    std::cout << "XYO SDK initialized successfully in Conan test package\n";
    return 0;
}
