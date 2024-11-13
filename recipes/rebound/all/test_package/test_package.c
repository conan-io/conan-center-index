#include "rebound.h"
#include <stdio.h>
#include <stdlib.h>


// Simplified from the simplest.c example in the REBOUND source code.
int main(int argc, char* argv[]) {
    struct reb_simulation* r = reb_simulation_create();

    reb_simulation_add_fmt(r, "m", 1.);                // Central object
    reb_simulation_add_fmt(r, "m a e", 1e-3, 1., 0.1); // Jupiter mass planet
    reb_simulation_add_fmt(r, "a e", 1.4, 0.1);        // Massless test particle

    // First integrate for 1 time units.
    reb_simulation_integrate(r, 1.);

    // Then output some coordinates and orbital elements.
    for (int i=0; i<r->N; i++){
        struct reb_particle p = r->particles[i];
        printf("%f %f %f\n", p.x, p.y, p.z);
    }
    struct reb_particle primary = r->particles[0];
    for (int i=1; i<r->N; i++){
        struct reb_particle p = r->particles[i];
        struct reb_orbit o = reb_orbit_from_particle(r->G, p, primary);
        printf("%f %f %f\n", o.a, o.e, o.f);
    }

    // Cleanup
    reb_simulation_free(r);
}
