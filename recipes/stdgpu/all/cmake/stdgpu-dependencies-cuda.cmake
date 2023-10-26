# Mimics the behavior of stdgpu-dependencies.cmake exported by stdgpu for the CUDA backend

find_dependency(CUDAToolkit 11.0 REQUIRED)
# Using ${stdgpu_LIBRARIES} to allow the target to be renamed using the "cmake_target_name" CMakeDeps property
target_link_libraries(${stdgpu_LIBRARIES} INTERFACE CUDA::cudart)
set_property(TARGET ${stdgpu_LIBRARIES} PROPERTY INTERFACE_COMPILE_FEATURES cuda_std_17)
