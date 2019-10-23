project(PackageTest)
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

message(${CONAN_LIBS})

add_executable(testPackage main.cpp)
target_link_libraries(testPackage ${CONAN_LIBS})

