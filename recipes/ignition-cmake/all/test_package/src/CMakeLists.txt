cmake_minimum_required(VERSION 3.1)
ign_add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ignition-cmake${IGN_CMAKE_VER}::utilities)
