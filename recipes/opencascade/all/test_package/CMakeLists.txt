cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Test components
find_package(OpenCASCADE COMPONENTS FoundationClasses ModelingData ModelingAlgorithms CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} TKMath TKGeomBase TKTopAlgo TKBRep)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

# Test global conan target
add_executable(${PROJECT_NAME}_global test_package.cpp)
target_link_libraries(${PROJECT_NAME}_global CONAN_PKG::opencascade)
set_property(TARGET ${PROJECT_NAME}_global PROPERTY CXX_STANDARD 11)
