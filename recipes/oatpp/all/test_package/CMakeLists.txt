cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(oatpp)

if ("${oatpp_VERSION}" EQUAL "1.0.0")
    add_executable(${PROJECT_NAME} example.cpp DeserializerTest_1_0_0.cpp)
else()
    add_executable(${PROJECT_NAME} example.cpp DeserializerTest.cpp)
endif()
target_link_libraries(${PROJECT_NAME} CONAN_PKG::oatpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
