#pragma once

#define ASSERT(x)                                                                                                       \
    do {                                                                                                                \
        if (!(x)) {                                                                                                     \
            throw std::runtime_error("assertion failed: " #x " is false at " __FILE__ ":" + std::to_string(__LINE__));  \
        }                                                                                                               \
    } while (0)

#define ASSERT_RAISES(exc, x)                                                                                           \
    do {                                                                                                                \
        try {                                                                                                           \
            x;                                                                                                          \
            throw std::runtime_error("assertion failed: no exception at " __FILE__ ":" + std::to_string(__LINE__));     \
        } catch (exc &e) {                                                                                              \
            std::cout << #exc << " exception message: " << e.what() << std::endl;                                       \
        }                                                                                                               \
    } while (0)

#define MARKER std::cout << "###MARKER###" << std::endl;
