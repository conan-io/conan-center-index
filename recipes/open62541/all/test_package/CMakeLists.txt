cmake_minimum_required(VERSION 3.12)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(open62541 REQUIRED CONFIG)
find_package(Threads REQUIRED)

find_package(Python3 REQUIRED)
set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})

# Output directory for Nodeset Compiler
set(GENERATE_OUTPUT_DIR "${CMAKE_BINARY_DIR}/src_generated/")
file(MAKE_DIRECTORY "${GENERATE_OUTPUT_DIR}")
include_directories("${GENERATE_OUTPUT_DIR}")
ua_generate_nodeset_and_datatypes(
    NAME "foo_flt"
    TARGET_PREFIX "${PROJECT_NAME}"
    FILE_CSV "${PROJECT_SOURCE_DIR}/FooFltModel.csv"
    FILE_BSD "${PROJECT_SOURCE_DIR}/FooFlt.Types.bsd"
    OUTPUT_DIR "${GENERATE_OUTPUT_DIR}"
    NAMESPACE_IDX 2  # This namespace index must match the order in which you are adding the nodeset in the source code
    #NAMESPACE_MAP "2:http://opcfoundation.org/UA/DI/"
    NAMESPACE_MAP "2:https://new.foo.com/zebra-compression/flattening-and-subspacefolding/UA/"
    FILE_NS "${PROJECT_SOURCE_DIR}/FooFlt.NodeSet2.xml"
    INTERNAL
)
# Previous macro automatically sets some variables which hold the generated source code files using the provided NAME
add_executable(${PROJECT_NAME}_nodeset
    ${UA_NODESET_FOO_FLT_SOURCES}
    ${UA_TYPES_FOO_FLT_SOURCES}
    test_package_nodeset.c
)
# Make sure the nodeset compiler is executed before compiling the main file
add_dependencies(${PROJECT_NAME}_nodeset ${PROJECT_NAME}-ns-foo_flt)
target_link_libraries(${PROJECT_NAME}_nodeset PRIVATE open62541::open62541)
