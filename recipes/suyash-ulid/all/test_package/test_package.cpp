#include <iostream>

#include "ulid.hh"

int main(void) {
    ulid::ULID ulid = ulid::Create(1484581420, []() { return 4; });
    std::string str = ulid::Marshal(ulid);
    std::cout << str << '\n';  // 0001C7STHC0G2081040G208104

    return EXIT_SUCCESS;
}
