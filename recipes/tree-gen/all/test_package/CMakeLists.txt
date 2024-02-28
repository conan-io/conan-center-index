cmake_minimum_required(VERSION 3.12)

project(PackageTest CXX)

find_package(tree-gen REQUIRED CONFIG)

# Generate the directory classes.
generate_tree_py(
    "${CMAKE_CURRENT_SOURCE_DIR}/res/directory.tree"
    "${CMAKE_CURRENT_SOURCE_DIR}/output/directory.actual.hpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/output/directory.actual.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/output/directory.actual.py"
)

message(STATUS
    "tree-gen executable PATH: $(tree-gen)"
)

add_executable(example
    "${CMAKE_CURRENT_SOURCE_DIR}/src/example.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/output/directory.actual.cpp"
)

target_compile_features(example
    PRIVATE cxx_std_17
)

target_link_libraries(example
    tree-gen::tree-gen
)
