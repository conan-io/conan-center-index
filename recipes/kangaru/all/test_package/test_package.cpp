#include <kangaru/kangaru.hpp>
#include <iostream>

/**
 * This example only show basic usage of services and the conatainer.
 */

// Normal classes with dependency between them
struct Camera {};

struct Scene {
	Camera& camera;
};

// This is the configuration of our classes.
// Structure and dependency graph is defined here.

// Camera is a single service so the service has a shared instance.
struct CameraService : kgr::single_service<Camera> {};

// Scene is not single, so the container return scenes by value.
// Also, we depends on a camera to be constructed.
struct SceneService : kgr::service<Scene, kgr::dependency<CameraService>> {};

int main()
{
	kgr::container container;
	
	// The service function return instances of the normal classes.
	Scene scene = container.service<SceneService>();
	Camera& camera = container.service<CameraService>();
	
	std::cout
		<< std::boolalpha
		<< (&scene.camera == &camera) << std::endl; // outputs true
}
