#include <CODE.h>
#include <cassert>

int main()
{
  chai3d::cWorld *world = new chai3d::cWorld();
  world->m_name = "WorldConanTest";

  assert(world->getNumChildren() == 0);

  cODEWorld *odeWorld = new cODEWorld(world);
  world->addChild(odeWorld);
  odeWorld->m_name = "RigidBodyWorldConanTest";
  chai3d::cVector3d gravity(0.0, 0.0, -9.81);
  odeWorld->setGravity(gravity);

  assert(world->getNumChildren() == 1 && odeWorld->getNumChildren() == 0);
  assert(gravity.equals(odeWorld->getGravity()));

  cODEGenericBody *odeBox = new cODEGenericBody(odeWorld);
  odeBox->m_name = "rigidBoxConanTest";
  odeBox->createDynamicBox(0.4, 0.4, 0.4);
  odeBox->setMass(0.03);

  assert(world->getNumChildren() == 1 && odeWorld->getNumChildren() == 1);
  assert(odeBox->getMass() == 0.03);

  delete world;
  world = nullptr;

  return EXIT_SUCCESS;
}
