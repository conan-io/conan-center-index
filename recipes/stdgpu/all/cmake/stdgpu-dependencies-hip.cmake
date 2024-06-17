# Mimics the behavior of stdgpu-dependencies.cmake exported by stdgpu for the HIP backend

find_dependency(thrust 1.9.9 REQUIRED)

find_dependency(hip 5.1 REQUIRED)

# Using ${stdgpu_LIBRARIES} to allow the target to be renamed using the "cmake_target_name" CMakeDeps property
target_link_libraries(${stdgpu_LIBRARIES} INTERFACE hip::host)
set_property(TARGET ${stdgpu_LIBRARIES} PROPERTY INTERFACE_COMPILE_FEATURES hip_std_17)
