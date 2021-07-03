#include <chai3d.h>
#include <cassert>

int main()
{
  chai3d::cWorld *world = new chai3d::cWorld();
  world->m_name = "WorldConanTest";
  world->m_backgroundColor.setWhite();

  assert(world->getNumChildren() == 0);

  chai3d::cCamera *camera = new chai3d::cCamera(world);
  world->addChild(camera);
  camera->m_name = "CameraConanTest";
  camera->set(chai3d::cVector3d(0.5, 0.0, 0.0),
              chai3d::cVector3d(0.0, 0.0, 0.0),
              chai3d::cVector3d(0.0, 0.0, 1.0));
  camera->setClippingPlanes(0.01, 10.0);

  assert(world->getNumChildren() == 1);
  assert(camera->getNearClippingPlane() == 0.01);

  chai3d::cDirectionalLight *light = new chai3d::cDirectionalLight(world);
  world->addChild(light);
  light->m_name = "DirLightConanTest";
  light->setEnabled(true);
  chai3d::cVector3d direction(-1.0, 0.0, 0.0);
  light->setDir(direction.get(0), direction.get(1), direction.get(2));

  assert(world->getNumChildren() == 2);
  assert(direction.equals(light->getDir()));

  delete world;
  world = nullptr;

  return EXIT_SUCCESS;
}
