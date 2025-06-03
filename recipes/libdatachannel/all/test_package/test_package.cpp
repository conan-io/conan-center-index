#include <cstdlib>
#include <rtc/rtc.hpp>
#include <iostream>


int main(void) {
    rtc::InitLogger(rtc::LogLevel::Debug);
    return EXIT_SUCCESS;
}
