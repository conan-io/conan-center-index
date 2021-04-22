cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(jsoncpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(JSONCPP_SHARED)
    target_link_libraries(${PROJECT_NAME} jsoncpp_lib)
else()
    target_link_libraries(${PROJECT_NAME} jsoncpp_static)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
