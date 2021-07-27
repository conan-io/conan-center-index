cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)
find_package(OMPL REQUIRED)

if (APPLE)
    set(CMAKE_INSTALL_RPATH "@executable_path" "@executable_path/../lib")
elseif(NOT WIN32) # Linux
    set(CMAKE_INSTALL_RPATH "$ORIGIN" "$ORIGIN/../lib")
endif() # windows, the library stays in bin folder with the executables
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

add_executable(example example.cpp)
target_link_libraries(example ompl::ompl)
