#include <iostream>

#include "PxConfig.h"
#include "PxPhysicsAPI.h"

#define PVD_HOST "127.0.0.1"
#define PX_RELEASE(x) if (x) {x->release(); x = NULL;}

using namespace physx;

PxDefaultAllocator gAllocator;
PxDefaultErrorCallback gErrorCallback;

PxFoundation *gFoundation = NULL;
PxPhysics *gPhysics = NULL;

PxDefaultCpuDispatcher *gDispatcher = NULL;
PxScene *gScene = NULL;

PxMaterial *gMaterial = NULL;

PxPvd *gPvd = NULL;

#if PX_SUPPORT_GPU_PHYSX
PxCudaContextManager *gCudaContextManager = NULL;
#endif

PxReal stackZ = 10.0f;

PxRigidDynamic *createDynamic(const PxTransform &t, const PxGeometry &geometry, const PxVec3 &velocity = PxVec3(0)) {
  PxRigidDynamic *dynamic = PxCreateDynamic(*gPhysics, t, geometry, *gMaterial, 10.0f);
  dynamic->setAngularDamping(0.5f);
  dynamic->setLinearVelocity(velocity);
  gScene->addActor(*dynamic);
  return dynamic;
}

void createStack(const PxTransform &t, PxU32 size, PxReal halfExtent) {
  PxShape *shape = gPhysics->createShape(PxBoxGeometry(halfExtent, halfExtent, halfExtent), *gMaterial);
  for (PxU32 i = 0; i < size; ++i) {
    for (PxU32 j = 0;j < size - i; ++j) {
      PxTransform localTm(PxVec3(PxReal(j * 2) - PxReal(size - i), PxReal(i * 2 + 1), 0) * halfExtent);
      PxRigidDynamic *body = gPhysics->createRigidDynamic(t.transform(localTm));
      body->attachShape(*shape);
      PxRigidBodyExt::updateMassAndInertia(*body, 10.0f);
      gScene->addActor(*body);
    }
  }
  shape->release();
}

void initPhysics() {
  gFoundation = PxCreateFoundation(PX_PHYSICS_VERSION, gAllocator, gErrorCallback);

  gPvd = PxCreatePvd(*gFoundation);
  PxPvdTransport *transport = PxDefaultPvdSocketTransportCreate(PVD_HOST, 5425, 10);
  gPvd->connect(*transport, PxPvdInstrumentationFlag::ePROFILE);

  gPhysics = PxCreatePhysics(PX_PHYSICS_VERSION, *gFoundation, PxTolerancesScale(), true, gPvd);

  PxSceneDesc sceneDesc(gPhysics->getTolerancesScale());
  sceneDesc.gravity = PxVec3(0.0f, -9.81f, 0.0f);
  gDispatcher = PxDefaultCpuDispatcherCreate(4);
  sceneDesc.cpuDispatcher = gDispatcher;
  sceneDesc.filterShader = PxDefaultSimulationFilterShader;

#if PX_SUPPORT_GPU_PHYSX
  PxCudaContextManagerDesc cudaContextManagerDesc;
  cudaContextManagerDesc.interopMode = PxCudaInteropMode::NO_INTEROP;
  gCudaContextManager = PxCreateCudaContextManager(*gFoundation, cudaContextManagerDesc, PxGetProfilerCallback());	//Create the CUDA context manager, required for GRB to dispatch CUDA kernels.
  if (gCudaContextManager) {
    if (!gCudaContextManager->contextIsValid()) {
      gCudaContextManager->release();
      gCudaContextManager = NULL;
    }
  }
  sceneDesc.cudaContextManager = gCudaContextManager; //Set the CUDA context manager, used by GRB.

  sceneDesc.flags |= PxSceneFlag::eENABLE_GPU_DYNAMICS; //Enable GPU dynamics - without this enabled, simulation (contact gen and solver) will run on the CPU.
  sceneDesc.flags |= PxSceneFlag::eENABLE_PCM; //Enable PCM. PCM NP is supported on GPU. Legacy contact gen will fall back to CPU
  sceneDesc.flags |= PxSceneFlag::eENABLE_STABILIZATION; //Improve solver stability by enabling post-stabilization.
  sceneDesc.broadPhaseType = PxBroadPhaseType::eGPU; //Enable GPU broad phase. Without this set, broad phase will run on the CPU.
  sceneDesc.gpuMaxNumPartitions = 8; //Defines the maximum number of partitions used by the solver. Only power-of-2 values are valid.
                                    //A value of 8 generally gives best balance between performance and stability.
#endif

  gScene = gPhysics->createScene(sceneDesc);

  PxPvdSceneClient *pvdClient = gScene->getScenePvdClient();
  if (pvdClient) {
    pvdClient->setScenePvdFlag(PxPvdSceneFlag::eTRANSMIT_CONSTRAINTS, true);
    pvdClient->setScenePvdFlag(PxPvdSceneFlag::eTRANSMIT_CONTACTS, true);
    pvdClient->setScenePvdFlag(PxPvdSceneFlag::eTRANSMIT_SCENEQUERIES, true);
  }
  gMaterial = gPhysics->createMaterial(0.5f, 0.5f, 0.6f);

  PxRigidStatic *groundPlane = PxCreatePlane(*gPhysics, PxPlane(0,1,0,0), *gMaterial);
  gScene->addActor(*groundPlane);

  for (PxU32 i = 0; i < 40; ++i) {
    createStack(PxTransform(PxVec3(0, 0, stackZ -= 10.0f)), 20, 1.0f);
  }

  PxRigidDynamic *ball = createDynamic(PxTransform(PxVec3(0,20,100)), PxSphereGeometry(5), PxVec3(0,-25,-100));
  PxRigidBodyExt::updateMassAndInertia(*ball, 1000.f);
}

void stepPhysics() {
  gScene->simulate(1.0f / 60.0f);
  gScene->fetchResults(true);
}

void cleanupPhysics() {
  PX_RELEASE(gScene);
  PX_RELEASE(gDispatcher);
  PX_RELEASE(gPhysics);
  if (gPvd) {
    PxPvdTransport *transport = gPvd->getTransport();
    gPvd->release();
    gPvd = NULL;
    PX_RELEASE(transport);
  }
#if PX_SUPPORT_GPU_PHYSX
  PX_RELEASE(gCudaContextManager);
#endif
  PX_RELEASE(gFoundation);
}

int main(int, char **) {
  static const PxU32 frameCount = 100;
  initPhysics();
  for (PxU32 i = 0; i < frameCount; ++i) {
    stepPhysics();
  }
  cleanupPhysics();

  std::cout << "Test of PhysX "
            << PX_PHYSICS_VERSION_MAJOR << "." << PX_PHYSICS_VERSION_MINOR << "." << PX_PHYSICS_VERSION_BUGFIX
            << " done.\n"
            << std::endl;

  return 0;
}
