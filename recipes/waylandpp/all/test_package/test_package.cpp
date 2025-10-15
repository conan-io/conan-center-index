#include <wayland-client.hpp>
#include <iostream>

int main(int argc, char **argv) {
    const auto display = wayland::display_t{};
    if (!display) {
	    std::cerr << "Can't connect to display\n";
    }
    else {
        std::cout << "connected to display fd: " << display.get_fd() << "\n";
    }

    exit(0);
}
