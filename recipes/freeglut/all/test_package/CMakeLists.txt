cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(FreeGLUT REQUIRED CONFIG)
find_package(OpenGL REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET FreeGLUT::freeglut_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE FreeGLUT::freeglut_static OpenGL::GL)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE FreeGLUT::freeglut OpenGL::GL)
endif()
