#include <handoffkit/handoffkit_core.hpp>

#include <cstdlib>
#include <iostream>
#include <string>

int main() {
    using namespace handoffkit;

    EchoProvider provider("echo");
    Agent agent("Consumer", "Uses handoffkit core", provider.as_any());
    auto out = agent.run("Validate Conan package");
    if (!out) {
        std::cerr << out.error().message << "\n";
        return EXIT_FAILURE;
    }

    const std::string ver = version();
    if (ver.empty()) {
        return EXIT_FAILURE;
    }
    std::cout << "handoffkit " << ver << " ok\n";
    return EXIT_SUCCESS;
}
