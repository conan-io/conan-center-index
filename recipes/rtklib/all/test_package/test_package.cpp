#include <rtklib.h>
#undef lock

#include <cstdlib>
#include <iostream>

// Extern functions meant to be defined by the user
extern int showmsg(const char *format, ...) { return 0; }
extern void settspan(gtime_t ts, gtime_t te) {}
extern void settime(gtime_t time) {}

int main() {
    int week = 0;
    double sec = time2gpst(timeget(), &week);
    std::cout << "Current GPS time: week " << week << ", " << sec << " seconds of week"
              << std::endl;
    return EXIT_SUCCESS;
}
