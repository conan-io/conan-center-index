cmake_minimum_required(VERSION 3.12)

project(PackageTest CXX)

find_package(tree-gen REQUIRED CONFIG)

find_program(TREE_GEN_EXECUTABLE tree-gen REQUIRED)

# Generate the directory classes.
generate_tree_py(
    "${TREE_GEN_EXECUTABLE}"
    "${CMAKE_CURRENT_SOURCE_DIR}/res/directory.tree"
    "${CMAKE_CURRENT_BINARY_DIR}/directory.hpp"
    "${CMAKE_CURRENT_BINARY_DIR}/directory.cpp"
    "${CMAKE_CURRENT_BINARY_DIR}/directory.py"
)

add_executable(test_package
    "${CMAKE_CURRENT_SOURCE_DIR}/src/test_package.cpp"
    "${CMAKE_CURRENT_BINARY_DIR}/directory.cpp"
)

target_include_directories(test_package
    PRIVATE "${CMAKE_CURRENT_BINARY_DIR}"
    PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src"
)
target_compile_features(test_package PRIVATE cxx_std_17)
target_link_libraries(test_package PRIVATE tree-gen::tree-gen)
