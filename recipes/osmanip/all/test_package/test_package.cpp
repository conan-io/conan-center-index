// This code is a part of upstream example code.
// https://github.com/JustWhit3/osmanip/blob/v4.0.0/examples/progressbar.cpp

// My headers
#include "osmanip/progressbar/multi_progress_bar.hpp"
#include "osmanip/progressbar/progress_bar.hpp"
#ifdef _WIN32
#include "osmanip/utility/windows.hpp"
#endif

// Since 4.1.0, options.hpp for `osm::OPTION` is added.
#if __has_include("osmanip/utility/options.hpp")
#  include "osmanip/utility/options.hpp"
#endif

// STD headers
#include <chrono>
#include <iostream>
#include <thread>

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
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        percentage_bar.update(i);
        // Do some operations...
    }
    std::cout << "\n\n";

    // Percentage bar with message and different style:
    osm::ProgressBar<float> percentage_bar_2(1.2f, 4.4f);
    percentage_bar_2.setMessage("processing...");
    percentage_bar_2.setStyle("indicator", "/100");

    std::cout << "This is a percentage bar with message and the /100 style: "
              << "\n";
    for (float i = percentage_bar_2.getMin(); i < percentage_bar_2.getMax(); i += 0.1f) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        percentage_bar_2.update(i);
        // Do some operations...
    }
    std::cout << "\n\n";

    // Percentage bar with time consuming info:
    percentage_bar.resetMessage();
    percentage_bar.setStyle("indicator", "%");

    std::cout << "This is a percentage bar with time consuming info: "
              << "\n";
    for (int i = percentage_bar.getMin(); i < percentage_bar.getMax(); i++) {
        percentage_bar.setBegin();
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        percentage_bar.update(i);
        // Do some operations...
        percentage_bar.setEnd();
    }
    std::cout << "\n"
              << "Time needed to complete the previous loop: " << percentage_bar.getTime() << " ms."
              << "\n\n";

    // Percentage bar with estimated time left:
    percentage_bar.setMin(2);
    percentage_bar.setMax(121);
    percentage_bar.setRemainingTimeFlag("on");
    percentage_bar.resetRemainingTime();

    std::cout << "This is a percentage bar with time-remaining info: "
              << "\n";
    for (int i = percentage_bar.getMin(); i < percentage_bar.getMax(); i++) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        percentage_bar.update(i);
        // Do some operations...
    }
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
