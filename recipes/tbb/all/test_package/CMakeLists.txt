cmake_minimum_required(VERSION 2.8.12)
PROJECT(TbbExample CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

ADD_EXECUTABLE(example main.cpp)
TARGET_LINK_LIBRARIES(example ${CONAN_LIBS})
SET_PROPERTY(TARGET example PROPERTY CXX_STANDARD 11)
