#include <clix/cli.hpp>
#include <clix/platform.hpp>

int main(int argc, char** argv) {
    auto info = clix::platform::current_info();
    if (!info.has_filesystem || !info.has_process_environment) {
        return 1;
    }

    clix::CLI cli("conan-center-test", "0.0.0");
    auto& echo = cli.command("echo").description("Echo the provided value.");
    echo.arg("value").description("Value to accept.");
    echo.action([](const clix::Invocation&) {});
    return cli.run(argc, argv);
}
