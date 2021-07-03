#include <CBullet.h>
#include <cassert>

int main()
{
  chai3d::cBulletWorld *world = new chai3d::cBulletWorld();
  world->m_name = "BulletWorldConanTest";
  chai3d::cVector3d gravity(0.0, 0.0, -9.8);
  world->setGravity(0.0, 0.0, -9.8);

  assert(gravity.equals(world->getGravity()));

  chai3d::cCamera *camera = new chai3d::cCamera(world);
  world->addChild(camera);
  camera->m_name = "CameraConanTest";
  camera->set(chai3d::cVector3d(0.5, 0.0, 0.0),
              chai3d::cVector3d(0.0, 0.0, 0.0),
              chai3d::cVector3d(0.0, 0.0, 1.0));
  camera->setClippingPlanes(0.01, 10.0);

  assert(world->getNumChildren() == 1);

  chai3d::cBulletBox *bulletBox = new chai3d::cBulletBox(world, 0.4, 0.4, 0.4);
  world->addChild(bulletBox);
  bulletBox->m_name = "BulletBoxConanTest";
  bulletBox->setSurfaceFriction(0.4);

  assert(world->getNumChildren() == 2);

  delete world;
  world = nullptr;

  return EXIT_SUCCESS;
}
