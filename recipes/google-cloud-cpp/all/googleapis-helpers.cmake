cmake_minimum_required(VERSION 3.7)

set(_gRPC_CPP_PLUGIN ${GRPC_CPP_PLUGIN_PROGRAM})
set(_gRPC_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)

function(protobuf_generate_grpc_cpp FILE_LOCATION OUT_SOURCES)
    set(_protobuf_include_path -I . -I ${CONAN_GOOGLEAPIS_PROTOS})

    get_filename_component(FILE_DIRECTORY ${FILE_LOCATION} DIRECTORY)
    get_filename_component(FILE_NAME ${FILE_LOCATION} NAME_WLE)
    file(RELATIVE_PATH REL_DIRECTORY ${CONAN_GOOGLEAPIS_PROTOS} ${FILE_DIRECTORY})

    set(${OUT_SOURCES} "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.grpc.pb.cc" "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.grpc.pb.h" PARENT_SCOPE)

    add_custom_command(
        OUTPUT "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.grpc.pb.cc"
            "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.grpc.pb.h"
        COMMAND ${_gRPC_PROTOBUF_PROTOC}
        ARGS --grpc_out=generate_mock_code=true:${_gRPC_PROTO_GENS_DIR}
            --plugin=protoc-gen-grpc=${_gRPC_CPP_PLUGIN}
            ${_protobuf_include_path}
            ${FILE_LOCATION}
        # DEPENDS ${_gRPC_PROTOBUF_PROTOC} gRPC::grpc_cpp_plugin
        COMMENT "Running gRPC C++ protocol buffer compiler for ${FILE_LOCATION}"
        )
endfunction()

function(protobuf_generate_cpp FILE_LOCATION OUT_SOURCES_PROTO_CPP)
    set(_protobuf_include_path -I . -I ${CONAN_GOOGLEAPIS_PROTOS})

    get_filename_component(FILE_DIRECTORY ${FILE_LOCATION} DIRECTORY)
    get_filename_component(FILE_NAME ${FILE_LOCATION} NAME_WLE)
    file(RELATIVE_PATH REL_DIRECTORY ${CONAN_GOOGLEAPIS_PROTOS} ${FILE_DIRECTORY})

    set(${OUT_SOURCES_PROTO_CPP} "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.pb.cc" "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.pb.h" PARENT_SCOPE)

    add_custom_command(
        OUTPUT "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.pb.cc"
            "${_gRPC_PROTO_GENS_DIR}/${REL_DIRECTORY}/${FILE_NAME}.pb.h"
        COMMAND ${_gRPC_PROTOBUF_PROTOC}
        ARGS --cpp_out=${_gRPC_PROTO_GENS_DIR}
            ${_protobuf_include_path}
            ${FILE_LOCATION}
        # DEPENDS ${_gRPC_PROTOBUF_PROTOC} gRPC::grpc_cpp_plugin
        COMMENT "Running C++ protocol buffer compiler for ${FILE_LOCATION}"
        )
endfunction()

function(googleapis_grpc_proto_library TARGET_SHORT_NAME PROTO_DIRS)
    cmake_parse_arguments(PARSE_ARGV 1 INPUT "" "" "GRPC_PROTOS_DIRS;GRPC_PROTOS;PROTOS_DIRS;PROTOS")

    set(SOURCES "")

    # Generate GRPC_PROTOS
    set(GRPC_PROTO_SOURCES ${INPUT_GRPC_PROTOS})
    foreach(ITEM ${INPUT_GRPC_PROTOS_DIRS})
        file(GLOB_RECURSE GRPC_PROTO_FILES ${ITEM}/*)
        list(APPEND GRPC_PROTO_SOURCES ${GRPC_PROTO_FILES})
    endforeach()

    list(LENGTH GRPC_PROTO_SOURCES GRPC_PROTO_SOURCES_LENGTH)
    message(STATUS "Found ${GRPC_PROTO_SOURCES_LENGTH} grpc-protos for target ${TARGET_SHORT_NAME}")

    foreach(ITEM ${GRPC_PROTO_SOURCES})
        protobuf_generate_grpc_cpp(${ITEM} OUT_SOURCES)
        list(APPEND SOURCES ${OUT_SOURCES})
    endforeach()

    # Generate PROTOS
    set(PROTO_SOURCES ${INPUT_PROTOS})
    foreach(ITEM ${INPUT_PROTOS_DIRS})
        file(GLOB_RECURSE PROTO_FILES ${ITEM}/*)
        list(APPEND PROTO_SOURCES ${PROTO_FILES})
    endforeach()

    list(LENGTH PROTO_SOURCES PROTO_SOURCES_LENGTH)
    message(STATUS "Found ${PROTO_SOURCES_LENGTH} protos for target ${TARGET_SHORT_NAME}")

    foreach(ITEM ${PROTO_SOURCES})
        protobuf_generate_cpp(${ITEM} OUT_SOURCES)
        list(APPEND SOURCES ${OUT_SOURCES})
    endforeach()

    add_library(google_cloud_cpp_${TARGET_SHORT_NAME} ${SOURCES})
    target_compile_features(google_cloud_cpp_${TARGET_SHORT_NAME} PUBLIC cxx_std_11)
    target_include_directories(google_cloud_cpp_${TARGET_SHORT_NAME} PUBLIC 
        $<BUILD_INTERFACE:${_gRPC_PROTO_GENS_DIR}>
        $<INSTALL_INTERFACE:include/>)
    target_link_libraries(google_cloud_cpp_${TARGET_SHORT_NAME} PUBLIC googleapis::googleapis gRPC::gRPC)
    
    set_target_properties(
            "google_cloud_cpp_${TARGET_SHORT_NAME}"
            PROPERTIES EXPORT_NAME google-cloud-cpp::${TARGET_SHORT_NAME}
                       VERSION ${PROJECT_VERSION}
                       SOVERSION ${PROJECT_VERSION_MAJOR})
    add_library("google-cloud-cpp::${TARGET_SHORT_NAME}" ALIAS
                "google_cloud_cpp_${TARGET_SHORT_NAME}")

    list(APPEND GOOGLEAPIS_GRPC_PROTOS_TARGETS google_cloud_cpp_${TARGET_SHORT_NAME})
    set(GOOGLEAPIS_GRPC_PROTOS_TARGETS ${GOOGLEAPIS_GRPC_PROTOS_TARGETS} PARENT_SCOPE)
endfunction()
