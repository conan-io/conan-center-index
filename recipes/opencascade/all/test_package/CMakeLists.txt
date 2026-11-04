cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

# Test components
find_package(OpenCASCADE REQUIRED FoundationClasses ModelingData ModelingAlgorithms CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE TKMath TKGeomBase TKTopAlgo TKBRep)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

# Test global conan target
add_executable(${PROJECT_NAME}_global test_package.cpp)
target_link_libraries(${PROJECT_NAME}_global PRIVATE opencascade::opencascade)
target_compile_features(${PROJECT_NAME}_global PRIVATE cxx_std_11)
