#include <cstdlib>
#include "keypop/card/ChannelControl.hpp"

int main(void) {
    /* Minimal usage exercising the header-only target: resolves an enum
     * constant by value, which throws on failure. */
    const auto control = keypop::card::valueOf(static_cast<int>(keypop::card::ChannelControl::CLOSE_AFTER));

    return control == keypop::card::ChannelControl::CLOSE_AFTER ? EXIT_SUCCESS : EXIT_FAILURE;
}
