cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(CLHEP REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(TARGET CLHEP::CLHEPS)
    target_link_libraries(${PROJECT_NAME} PRIVATE CLHEP::CLHEPS)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE CLHEP::CLHEP)
endif()
