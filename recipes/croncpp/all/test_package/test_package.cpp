#include <iostream>
#include <ctime>

#include "croncpp.h"

int main(int argc, const char** argv) {
    try {
        auto cron = cron::make_cron("* 0/5 * * * ?");

        auto now = std::time(0);
        auto next = cron::cron_next(cron, now);
        std::cout << (next - now) << "[sec]" << std::endl;
        return 0;
    } catch (cron::bad_cronexpr const& ex) {
        std::cerr << ex.what() << std::endl;
    }
    return -1;
}
