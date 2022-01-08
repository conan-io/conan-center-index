CMAKE_MINIMUM_REQUIRED(VERSION 3.12)

PROJECT(test_package VERSION 1.0.0 LANGUAGES CXX)
INCLUDE(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
find_package(flatbush CONFIG REQUIRED)

ADD_EXECUTABLE(${PROJECT_NAME} "test_package.cpp")

TARGET_LINK_LIBRARIES(${PROJECT_NAME} flatbush::flatbush)
