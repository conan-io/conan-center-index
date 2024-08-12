#include <iostream>
#include "ftp/client.hpp"

int main(void) {
    try {
        ftp::client client;
        client.get_current_directory();
        client.disconnect();
    }
    catch (const std::exception & ex) {
        std::cerr << ex.what() << std::endl;
    }
    return 0;
}
