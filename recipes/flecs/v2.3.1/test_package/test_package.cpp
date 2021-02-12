#include <flecs.h>
#include <iostream>

struct Position { float x; float y; };

int main(int argc, char *argv[])
{
    flecs::world world(argc, argv);

    auto e = world.entity("MyEntity");
    e.set<Position>({10, 20});

    const Position *p = e.get<Position>();

    std::cout << "Position of " << e.name() << " is {" << p->x << ", " << p->y << "}\n";
}
