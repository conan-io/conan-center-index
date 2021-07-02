cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

configure_file(cube.obj cube.obj COPYONLY)
configure_file(cube.mtl cube.mtl COPYONLY)

find_package(tinyobjloader REQUIRED CONFIG)

string(FIND "${CONAN_TINYOBJLOADER_ROOT}" "2." IS_2x)
if ("${IS_2x}" EQUAL "-1")
    add_executable(${PROJECT_NAME} test_package_1.cpp)
else()
    add_executable(${PROJECT_NAME} test_package_2.cpp)
endif()

if(TARGET tinyobjloader_double)
    target_link_libraries(${PROJECT_NAME} tinyobjloader_double)
else()
    target_link_libraries(${PROJECT_NAME} tinyobjloader)
endif()
