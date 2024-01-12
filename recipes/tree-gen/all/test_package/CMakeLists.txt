cmake_minimum_required(VERSION 3.12)
project(TreeGenTestPackage CXX)
find_package(tree-gen CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example PUBLIC
    tree-gen::tree-gen
)
message(STATUS
    "[${PROJECT_NAME}] Target include directories:\n"
    "      tree-gen_INCLUDE_DIRS: ${tree-gen_INCLUDE_DIRS}\n"
)
