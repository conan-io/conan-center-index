cmake_minimum_required(VERSION 3.1.3) # 3.1.3 is first fully functional cross-platform version with Targets
project(test_vtk_package)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::vtk)

