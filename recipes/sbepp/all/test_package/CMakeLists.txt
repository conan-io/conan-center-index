cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(sbepp REQUIRED CONFIG)

# test `sbepp::sbeppc` executable
if(TARGET sbepp::sbeppc)
    set(sbeppc_test_name "test_sbeppc")

    sbeppc_compile_schema(
        TARGET_NAME compiled_schema
        SCHEMA_FILE "${CMAKE_CURRENT_LIST_DIR}/test_schema.xml"
    )

    add_executable(${sbeppc_test_name})
    target_sources(${sbeppc_test_name} PRIVATE test_sbeppc.cpp)

    target_link_libraries(${sbeppc_test_name} PRIVATE compiled_schema)
    target_compile_features(${sbeppc_test_name} PRIVATE cxx_std_11)
endif()

# test `sbepp::sbepp` header-only library
add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE test_sbepp.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE sbepp::sbepp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
