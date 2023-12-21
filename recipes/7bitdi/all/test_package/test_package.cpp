#include <iostream>
#include <SevenBit/DI.hpp>

struct LibInfo {
    std::string getVersion() const { return _7BIT_DI_VERSION; }

    std::string getInfo() const { return "7bitdi version: " + getVersion(); }
};

template<class TProvider>
auto& extractProvider(TProvider& provider) {
    if constexpr (_7BIT_DI_VERSION_AS_NUMBER == 10000) {
        return *provider;
    } else {
        return provider;
    }
}

int main() {
    auto provider = sb::di::ServiceCollection{}.addSingleton<LibInfo>().buildServiceProvider();

    std::cout << extractProvider(provider).getService<LibInfo>().getInfo() << std::endl;
    return 0;
}
