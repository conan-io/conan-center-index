cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(FreeGLUT REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET FreeGLUT::freeglut_static)
    target_link_libraries(${PROJECT_NAME} FreeGLUT::freeglut_static)
else()
    target_link_libraries(${PROJECT_NAME} FreeGLUT::freeglut)
endif()
