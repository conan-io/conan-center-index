#include "ClpSimplex.hpp"

#include <stdio.h>

int main (int argc, const char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Need an argument\n");
        return 1;
    }
    ClpSimplex model;
    int status = model.readMps(argv[1]);
    if (status != 0) {
        model.primal();
    }
    return 0;
}
