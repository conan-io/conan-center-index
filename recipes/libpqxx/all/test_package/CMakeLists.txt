cmake_minimum_required(VERSION 3.8)

# Set `-mmacosx-version-min` to enable C++17 standard library support.
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")

project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libpqxx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} libpqxx::pqxx)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
