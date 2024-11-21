cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(protobuf CONFIG REQUIRED)

if (protobuf_LITE)
    set(PROTO_FILE addressbook-lite.proto)
else()
    set(PROTO_FILE addressbook.proto)
endif()
    
add_executable(${PROJECT_NAME} ${PROTO_FILE} test_package.cpp)

if(CONAN_TEST_USE_CXXSTD_14)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()

target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")

if (protobuf_LITE)
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotobuf-lite)
    set(PROTOBUF_PLUGIN_OPTIONS "lite")
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotobuf)

    # libprotoc always link libprotobuf, so we don't want to link with that
    # when using LITE version
    if(TARGET protobuf::libprotoc)
        target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotoc)
    endif()
endif()

if(NOT TARGET protobuf::protoc)
    message(FATAL_ERROR "protoc executable should have been defined as part of find_package(protobuf)")
endif()

if(NOT COMMAND protobuf_generate)
    message(FATAL_ERROR "protobuf_generate should have been defined as part of find_package(protobuf)")
endif()

protobuf_generate(TARGET ${PROJECT_NAME} PLUGIN_OPTIONS ${PROTOBUF_PLUGIN_OPTIONS})
