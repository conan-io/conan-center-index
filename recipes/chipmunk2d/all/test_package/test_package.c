#include "chipmunk/chipmunk.h"

int main()
{
    cpSpace *space = cpSpaceNew();
    cpSpaceSetGravity(space, cpv(0, -600));
    cpSpaceFree(space);
    return 0;
}
