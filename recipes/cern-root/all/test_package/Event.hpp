#ifndef TEST_PACKAGE_EVENT_HPP
#define TEST_PACKAGE_EVENT_HPP

#include "TLorentzVector.h"

class Particle {
    public:
        Particle();
        Particle(int _id, TLorentzVector _p4);
        ~Particle();

        int getID();
        void setID(int);

        TLorentzVector getP4();
        void setP4(TLorentzVector);
    private:
        int id;
        TLorentzVector p4;
};

class Event {
    public:
        Event();
        ~Event();
        std::vector<Particle> particles;
};

#endif
