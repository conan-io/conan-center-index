cmake_minimum_required(VERSION 3.1.3) # 3.1.3 is first fully functional cross-platform version with Targets
project(test_vtk_package)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::vtk)

# From oryginal recipe
# if(UNIX AND NOT APPLE)
#     TARGET_LINK_LIBRARIES(${PROJECT_NAME} m)
# endif()


#############################
# Below is working test for "cmake_find_package_multi" generator (above is for "cmake" generator).
#
# cmake_minimum_required(VERSION 3.1.3) # 3.1.3 is first fully functional cross-platform version with Targets
#
# set(CMAKE_CXX_STANDARD 11)
#
# project(test_vtk_package)
#
# find_package(VTK REQUIRED CONFIG)
#
# add_executable(${PROJECT_NAME} test_package.cpp)
# target_link_libraries(${PROJECT_NAME} VTK::VTK)
#

