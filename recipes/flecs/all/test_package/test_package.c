#include <flecs.h>

#include <stdio.h>

typedef struct {
    float x;
    float y;
} Position;

int main() {
    ecs_world_t *world = ecs_init();

    ECS_COMPONENT(world, Position);

    ecs_entity_t e = ecs_new_id(world);
    ecs_set(world, e, Position, {10.0f, 20.0f});

    const char *name = ecs_get_name(world, e);
    const Position *p = ecs_get(world, e, Position);
    printf("Position of %s is {%f, %f}\n", name, p->x, p->y);

    return 0;
}
