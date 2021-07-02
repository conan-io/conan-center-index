#include <string>

#include "continuable/continuable.hpp"

int main(int, char**) {
    cti::make_ready_continuable<std::string>("<html>...</html>");

    return 0;
}
