#include <gaia.h>

int main()
{
    gaia::ecs::World w;
    gaia::ecs::Entity e = w.add();
    (void) w.valid(e);
    return 0;
}
