#include "box3d/box3d.h"

int main(void) {
    b3WorldDef worldDef = b3DefaultWorldDef();
    worldDef.gravity = b3Vec3{ 0.0f, -10.0f, 0.0f };

    b3WorldId worldId = b3CreateWorld(&worldDef);

    b3BodyDef groundBodyDef = b3DefaultBodyDef();
    groundBodyDef.position = b3Vec3{ 0.0f, -10.0f, 0.0f };

    b3BodyId groundId = b3CreateBody(worldId, &groundBodyDef);

    b3BoxHull groundBox = b3MakeBoxHull(50.0f, 10.0f, 50.0f);

    b3ShapeDef groundShapeDef = b3DefaultShapeDef();
    b3CreateHullShape(groundId, &groundShapeDef, &groundBox.base);

    b3DestroyWorld(worldId);

    return 0;
}