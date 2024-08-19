cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(freenect2 REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE freenect2::freenect2)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

if (WITH_CUDA)
    cmake_minimum_required(VERSION 3.17)
    find_package(CUDAToolkit REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE CUDA::cudart)
endif()
