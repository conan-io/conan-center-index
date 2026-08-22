#include "CglProbing.hpp"

int main(int argc, char *argv[])
{
    CglProbing probing;
    probing.setLogLevel(0);
    probing.setUsingObjective(1);
    return probing.getUsingObjective() == 1 ? 0 : 1;
}
