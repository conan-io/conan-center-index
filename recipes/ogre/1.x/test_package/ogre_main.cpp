#include <OGRE/Ogre.h>
#include <iostream>

int main() {
    Ogre::RenderSystemCapabilities rc;
    rc.setNumTextureUnits(10);
    std::cout << "Hello from OgreMain component\n";
    std::cout << "number of texture units: " << rc.getNumTextureUnits() << "\n";

    Ogre::Radian rot{0.618};
    Ogre::Particle particle;
    particle.setDimensions(0, 0);

    return 0;
}
