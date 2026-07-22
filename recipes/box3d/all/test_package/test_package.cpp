#include "box3d/box3d.h"
#include <iostream>

int main(void) {
    auto version = b3GetVersion();
    auto major = version.major;
    auto minor = version.minor;
    auto revision = version.revision;
    std::cout << "Box3D version: " << major << "." << minor << "." << revision << std::endl;
    std::cout << "Is double precision: " << b3IsDoublePrecision() << std::endl;

    b3WorldDef worldDef = b3DefaultWorldDef();
    // This has undefined symbols if double precision is mismatched
    b3WorldId worldId = b3CreateWorld(&worldDef);
    b3DestroyWorld(worldId);

    return 0;
}
