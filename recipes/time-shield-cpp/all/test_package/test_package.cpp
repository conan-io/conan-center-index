#include <time_shield.hpp>
#include <time_shield/core.hpp>

#include <cstdlib>

int main() {
    const time_shield::ts_t timestamp = time_shield::to_timestamp(2026, 9, 12);
    const time_shield::DateTime date_time = time_shield::DateTime::from_unix_s(timestamp);
    return date_time.year() == 2026 ? EXIT_SUCCESS : EXIT_FAILURE;
}
