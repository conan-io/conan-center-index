cmake_minimum_required(VERSION 3.1)

project(test_package)

enable_language(CUDA)
find_package(nvcc REQUIRED)

# In case of conan <= 1.62
if (NOT CUDAToolkit_NVCC_EXECUTABLE)
    include("nvcc_toolchain")
endif()

add_executable(${PROJECT_NAME} test_package.cu)
target_link_libraries(${PROJECT_NAME} PRIVATE CUDA::cudart)
