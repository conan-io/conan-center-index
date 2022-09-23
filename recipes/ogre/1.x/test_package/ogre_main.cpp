#include <OGRE/OgreRenderSystemCapabilities.h>
#include <OGRE/OgreParticle.h>
#include <OGRE/OgrePrerequisites.h>
#include <iostream>

int main(int argc, char **argv) {
  Ogre::RenderSystemCapabilities rc;
  rc.setNumTextureUnits(10);
  std::cout << "Hello from OgreMain component\n";
  std::cout << "number of texture units: " << rc.getNumTextureUnits() << "\n";

  Ogre::Radian rot{0.618};
  Ogre::Particle particle;
  particle.resetDimensions();

  return 0;
}
