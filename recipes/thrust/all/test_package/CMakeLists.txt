cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(thrust CONFIG REQUIRED)

if (THRUST_BACKEND STREQUAL "CUDA")
    cmake_minimum_required(VERSION 3.18)
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    add_executable(${PROJECT_NAME} test_package.cu)
    target_link_libraries(${PROJECT_NAME} CUDA::cudart)
    if (CMAKE_VERSION VERSION_GREATER_EQUAL "3.24")
        set_target_properties(${PROJECT_NAME} PROPERTIES CUDA_ARCHITECTURES native)
    else()
        # Use the defaults from nvcc
        set_target_properties(${PROJECT_NAME} PROPERTIES CUDA_ARCHITECTURES OFF)
    endif()
else()
    add_executable(${PROJECT_NAME} test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} thrust::thrust)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
