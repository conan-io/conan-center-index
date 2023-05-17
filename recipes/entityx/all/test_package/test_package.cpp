#if defined(_WIN32)
#define NOMINMAX
#endif
#include <entityx/entityx.h>

#include <string>
#include <iostream>

int
main(int argc, char **argv)
{
	entityx::EntityX ex;
	entityx::Entity entity = ex.entities.create();
	std::cout << "Entity = " << entity;
	entity.destroy();
	return 0;
}
