#include <wayland-client.hpp>
#include <iostream>

int main(int argc, char **argv) {
    try {
        const auto display = wayland::display_t{};
        if (!display) {
	        throw std::runtime_error("Can't connect to display");
        }
        std::cout << "connected to display fd: " << display.get_fd() << '\n';
        exit(0);
    }
    catch (std::exception const &ex) {
        std::cerr << ex.what() << '\n';
    }

    return 0;
}
