// This code is a part of upstream example code.
// https://github.com/JustWhit3/osmanip/blob/v4.0.0/examples/progressbar.cpp

// My headers
#include "osmanip/progressbar/progress_bar.hpp"
#ifdef _WIN32
#include "osmanip/utility/windows.hpp"
#endif

// Since 4.1.0, options.hpp for `osm::OPTION` is added.
#if __has_include("osmanip/utility/options.hpp")
#  include "osmanip/utility/options.hpp"
#endif

// STD headers
#include <iostream>

//====================================================
//     Percentage bar
//====================================================
void
perc_bars() {
    std::cout << "\n"
              << "======================================================"
              << "\n"
              << "     PERCENTAGE BARS                                    "
              << "\n"
              << "======================================================"
              << "\n\n";

    // Normal percentage bar.
    osm::ProgressBar<int> percentage_bar;
    percentage_bar.setMin(5);
    percentage_bar.setMax(46);
    percentage_bar.setStyle("indicator", "%");

    std::cout << "This is a normal percentage bar: "
              << "\n";
    for (int i = percentage_bar.getMin(); i < percentage_bar.getMax(); i++) {
        percentage_bar.update(i);
        // Do some operations...
    }
    std::cout << "\n\n";
    std::cout << "\n\n";
}

//====================================================
//     Main
//====================================================
int main() {
#ifdef _WIN32
    osm::enableANSI();
#endif

    osm::OPTION(osm::CURSOR::OFF);

    perc_bars();         // Percentage bar.

    osm::OPTION(osm::CURSOR::ON);

#ifdef _WIN32
    osm::disableANSI();
#endif
}
