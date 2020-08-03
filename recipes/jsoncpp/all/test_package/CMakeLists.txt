cmake_minimum_required(VERSION 3.1)
project(test_package)

SET(CMAKE_CXX_STANDARD 11)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
SET(CMAKE_CXX_EXTENSIONS OFF)

find_package(JsonCpp REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} JsonCpp::JsonCpp)

if(JsonCpp_VERSION VERSION_LESS "1.0.0")
    # For versions 0.y.z, includes must be prefixed with "jsoncpp/"
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_JSONCPP_PREFIX)
endif()