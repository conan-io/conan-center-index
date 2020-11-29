#ifndef TEST_PACKAGE_EVENT_HPP
#define TEST_PACKAGE_EVENT_HPP

#include "Particle.hpp"

class Event {
    public:
        Event();
        ~Event();
        std::vector<Particle> particles;
};

#endif
