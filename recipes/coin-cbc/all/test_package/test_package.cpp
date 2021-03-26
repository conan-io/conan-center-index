#include "OsiCbcSolverInterface.hpp"

#include <cstdio>
#include <cstdlib>

int main(int argc, char *argv[])
{
    OsiCbcSolverInterface im;
    if (im.getNumCols() != 0) {
        fprintf(stderr, "Wrong #columns\n");
        return 1;
    }
    if (im.getModelPtr() == NULL) {
        fprintf(stderr, "Bad model ointer\n");
        return 1;
    }
    return 0;
}
