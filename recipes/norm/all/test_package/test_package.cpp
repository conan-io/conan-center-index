#include <cstdlib>
#include <iostream>

#include "normApi.h"
// Test to validate Conan package generated

int main(int /*argc*/, const char * /*argv*/ []) {
	NormInstanceHandle handle = NormCreateInstance();
	if(handle == NORM_INSTANCE_INVALID)
	{
		std::cout << "Failed to create handle" << std::endl;
		return EXIT_FAILURE;
	}
	std::cout << "Succesfully created handle" << std::endl;
	NormDestroyInstance(handle);
	return EXIT_SUCCESS;
}
