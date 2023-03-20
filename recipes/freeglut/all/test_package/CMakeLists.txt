cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(FreeGLUT REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET FreeGLUT::freeglut_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE FreeGLUT::freeglut_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE FreeGLUT::freeglut)
endif()
