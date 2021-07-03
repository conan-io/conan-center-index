#include <GEL3D.h>
#include <cassert>

int main()
{
  chai3d::cWorld *world = new chai3d::cWorld();
  world->m_name = "WorldConanTest";

  assert(world->getNumChildren() == 0);

  cGELWorld *gelWorld = new cGELWorld();
  world->addChild(gelWorld);
  gelWorld->m_name = "DeformableWorldConanTest";

  assert(world->getNumChildren() == 1 && gelWorld->getNumChildren() == 0);

  cGELMesh *defObject = new cGELMesh();
  defObject->m_name = "DeformableObjectConanTest";
  gelWorld->m_gelMeshes.push_front(defObject);
  defObject->m_useSkeletonModel = true;

  assert(world->getNumChildren() == 1 && gelWorld->getNumChildren() == 1);

  delete world;
  world = nullptr;

  return EXIT_SUCCESS;
}
