#include <cstdlib>
#include <iostream>
#include <time.h>
#include "iso8601.h"

int main(void)
{
    const char* dateTime = "1997-07-16T19:20:30.45+01:00";

    struct tm isoDateTime;
    int timezoneOffsetMin;
    if (ParseIso8601Datetime(dateTime, &isoDateTime, &timezoneOffsetMin))
    {
        std::cout << "Year: " << isoDateTime.tm_year + 1900 << "\n";
        std::cout << "Month: " << isoDateTime.tm_mon + 1 << "\n";
        std::cout << "Day: " << isoDateTime.tm_mday << "\n";
        std::cout << "Hour: " << isoDateTime.tm_hour << "\n";
        std::cout << "Minute: " << isoDateTime.tm_min << "\n";
        std::cout << "Second: " << isoDateTime.tm_sec << "\n";
        std::cout << "Timezone offset: " << timezoneOffsetMin << "\n";
    }
    else
    {
        std::cout << "Could not parse datetime " << dateTime << "\n";
    }
    return EXIT_SUCCESS;
}
