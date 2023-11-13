#include <string>

#include "continuable/continuable.hpp"

int main() {
    cti::make_ready_continuable<std::string>("<html>...</html>");

    return 0;
}
