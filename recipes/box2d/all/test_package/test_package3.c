#include "box2d/box2d.h"

int main() {
    b2WorldDef worldDef = b2DefaultWorldDef();

    worldDef.gravity = (b2Vec2){0.0f, -10.0f};
    b2WorldId worldId = b2CreateWorld(&worldDef);

    b2BodyDef groundBodyDef = b2DefaultBodyDef();
    groundBodyDef.position = (b2Vec2){0.0f, -10.0f};

    return 0;
}
