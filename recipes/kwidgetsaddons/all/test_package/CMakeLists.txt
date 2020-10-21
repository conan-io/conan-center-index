cmake_minimum_required(VERSION 3.5)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Qt5 CONFIG REQUIRED Widgets)

add_executable(example example.cpp)
target_link_libraries(example CONAN_PKG::kwidgetsaddons Qt5::Widgets)
