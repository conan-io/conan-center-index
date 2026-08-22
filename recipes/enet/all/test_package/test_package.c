#include <enet/enet.h>

int main (int argc, char ** argv) 
{
    if (enet_initialize () != 0)
    {
        return 1;
    }
    enet_deinitialize();
    return 0;
}
