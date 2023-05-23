#include "hsm/hsm.h"

#include <iostream>
#include <cassert>

// States
struct Locked {
};
struct Unlocked {
};

// Events
struct Push {
};
struct Coin {
};

// Guards
const auto noError = [](auto /*event*/, auto /*source*/, auto /*target*/) { return true; };

// Actions
constexpr auto beep
    = [](auto /*event*/, auto /*source*/, auto /*target*/) { std::cout << "beep!" << std::endl; };
constexpr auto blink = [](auto /*event*/, auto /*source*/, auto /*target*/) {
    std::cout << "blink, blink, blink!" << std::endl;
};

struct Turnstile {
    static constexpr auto make_transition_table()
    {
        // clang-format off
        return hsm::transition_table(
            // Source              + Event            [Guard]   / Action = Target
            // +-------------------+-----------------+---------+--------+----------------------+
            * hsm::state<Locked>   + hsm::event<Push>           / beep   = hsm::state<Locked>  ,
              hsm::state<Locked>   + hsm::event<Coin> [noError] / blink  = hsm::state<Unlocked>,
            // +--------------------+---------------------+---------+--------+------------------------+
              hsm::state<Unlocked> + hsm::event<Push> [noError]          = hsm::state<Locked>  ,
              hsm::state<Unlocked> + hsm::event<Coin>           / blink  = hsm::state<Unlocked>
            // +--------------------+---------------------+---------+--------+------------------------+                        
            );
        // clang-format on
    }
};

auto main() -> int
{
    hsm::sm<Turnstile> turnstileSm;

    // The turnstile is initially locked
    assert(turnstileSm.is(hsm::state<Locked>));

    // Inserting a coin unlocks it
    turnstileSm.process_event(Coin {});
    assert(turnstileSm.is(hsm::state<Unlocked>));

    // Entering the turnstile will lock it again
    turnstileSm.process_event(Push {});
    assert(turnstileSm.is(hsm::state<Locked>));

    return 0;
}
