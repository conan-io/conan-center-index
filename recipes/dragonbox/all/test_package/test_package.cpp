#include <cstdlib>
#include <iostream>

#include "dragonbox/dragonbox_to_chars.h"

int main(void) {
    constexpr int buffer_length = 1 + // for '\0'
        jkj::dragonbox::max_output_string_length<jkj::dragonbox::ieee754_binary64>;
    double x = 1.234;  // Also works for float
    char buffer[buffer_length];

    // Null-terminate the buffer and return the pointer to the null character
    // Hence, the length of the string is (end_ptr - buffer)
    // buffer is now { '1', '.', '2', '3', '4', 'E', '0', '\0', (garbages) }
    char* end_ptr = jkj::dragonbox::to_chars(x, buffer);

    // Does not null-terminate the buffer; returns the next-to-end pointer
    // buffer is now { '1', '.', '2', '3', '4', 'E', '0', (garbages) }
    // you can wrap the buffer with things like std::string_view
    end_ptr = jkj::dragonbox::to_chars_n(x, buffer);

    return 0;
}
