cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(stdgpu CONFIG REQUIRED)

if (STDGPU_BACKEND STREQUAL "CUDA")
    cmake_minimum_required(VERSION 3.18)
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    add_executable(${PROJECT_NAME} test_package.cu)
    target_link_libraries(${PROJECT_NAME} CUDA::cudart)
    set_target_properties(${PROJECT_NAME} PROPERTIES CUDA_ARCHITECTURES 61)
else()
add_executable(${PROJECT_NAME} test_package.cpp)
endif()

target_link_libraries(${PROJECT_NAME} stdgpu::stdgpu)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
