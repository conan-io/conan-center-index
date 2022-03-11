/* final_all_pp.cpp

   Simple libftdi-cpp usage

   This program is distributed under the GPL, version 2
*/

#include <ftdi.hpp>

#include <iostream>

int main(int argc, char **argv)
{
    int vid = 0x0403;
    int pid = 0x6001;

    // Print whole list
    ftdi_version_info version = ftdi_get_library_version();
    std::cout << "FTDI Library Version: " << version.version_str << "\n";

    Ftdi::Context context;
    Ftdi::List *devices = Ftdi::List::find_all(context, vid, pid);

    if (devices->empty()) {
        std::cout << "No FTDI devices found" << std::endl;
    }

    for (Ftdi::List::iterator it = devices->begin(); it != devices->end(); ++it) {
        std::cout << "FTDI (" << &*it << "): "
        << it->vendor() << ", "
        << it->description() << ", "
        << it->serial();

        // Open test
        if(it->open() == 0) {
           std::cout << " (Open OK)";
        }
        else {
           std::cout << " (Open FAILED)";
        }

        it->close();

        std::cout << "\n";
    }
    std::cout << std::endl;

    return EXIT_SUCCESS;
}
