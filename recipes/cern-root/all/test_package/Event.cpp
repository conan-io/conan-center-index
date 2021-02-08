#include "Event.hpp"

Event::Event() {}
Event::~Event() {}

Particle::Particle() {}

Particle::Particle(int _id, TLorentzVector _p4) : id(_id), p4(_p4) {}

Particle::~Particle() {}

int Particle::getID() { return id; }

void Particle::setID(int _id) { id = _id; }

TLorentzVector Particle::getP4() { return p4; }

void Particle::setP4(TLorentzVector _p4) { p4 = _p4; }
