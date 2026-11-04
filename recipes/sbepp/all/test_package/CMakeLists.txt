cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(sbepp REQUIRED CONFIG)

# test `sbepp::sbeppc` executable
if(TARGET sbepp::sbeppc)
    set(sbeppc_test_name "test_sbeppc")
    set(schema "test_schema")
    set(schema_path "${CMAKE_CURRENT_LIST_DIR}/${schema}.xml")

    add_executable(${sbeppc_test_name})
    target_sources(${sbeppc_test_name} PRIVATE test_sbeppc.cpp)
    target_compile_features(${sbeppc_test_name} PRIVATE cxx_std_11)

    # `sbeppc_compile_schema` was introduced only in `1.2.0`
    if(SBEPP_VERSION VERSION_GREATER_EQUAL "1.2.0")
        sbeppc_compile_schema(
            TARGET_NAME compiled_schema
            SCHEMA_FILE "${schema_path}"
        )

        target_link_libraries(${sbeppc_test_name} PRIVATE compiled_schema)
    else()
        set(output_file "${CMAKE_CURRENT_BINARY_DIR}/${schema}/${schema}.hpp")

        add_custom_command(
            OUTPUT "${output_file}"
            COMMAND $<TARGET_FILE:sbepp::sbeppc> "${schema_path}"
            DEPENDS "${schema_path}"
        )

        add_custom_target(compile_schema DEPENDS "${output_file}")
        add_dependencies(${sbeppc_test_name} compile_schema)
        target_include_directories(${sbeppc_test_name}
            SYSTEM PRIVATE
            "${CMAKE_CURRENT_BINARY_DIR}"
        )

        target_link_libraries(${sbeppc_test_name} PRIVATE sbepp::sbepp)
    endif()
endif()

# test `sbepp::sbepp` header-only library
add_executable(${PROJECT_NAME})
target_sources(${PROJECT_NAME} PRIVATE test_sbepp.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE sbepp::sbepp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
