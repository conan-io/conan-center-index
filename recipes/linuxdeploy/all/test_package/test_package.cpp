#include <iostream>
#include <linuxdeploy/util/util.h>
#include <linuxdeploy/desktopfile/exceptions.h>

int main() {
    std::cout << "\"which conan\": " << linuxdeploy::util::misc::which("conan").string() << std::endl;
    try {
        throw linuxdeploy::desktopfile::DesktopFileError("linuxdeploy-desktopfile is functional!");
    } catch (linuxdeploy::desktopfile::DesktopFileError e) {
        std::cout << e.what() << std::endl;
    }
    return 0;
}
