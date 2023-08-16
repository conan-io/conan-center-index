cmake_minimum_required(VERSION 3.8)

# Set `-mmacosx-version-min` to enable C++17 standard library support.
set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")

project(test_package LANGUAGES CXX)

find_package(libpqxx REQUIRED CONFIG)


add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE libpqxx::pqxx)
if(libpqxx_VERSION VERSION_LESS "7.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
