cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(jwt-cpp REQUIRED CONFIG)
find_package(picojson REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE jwt-cpp::jwt-cpp picojson::picojson)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
