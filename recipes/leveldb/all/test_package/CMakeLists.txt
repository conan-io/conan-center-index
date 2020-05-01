cmake_minimum_required(VERSION 3.2)
PROJECT(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

ADD_EXECUTABLE(example example.cpp example.hpp)
TARGET_LINK_LIBRARIES(example ${CONAN_LIBS})
