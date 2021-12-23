find_package(Protobuf REQUIRED) # protoc executable binary
find_package(ProtobufC REQUIRED) # protoc-gen-c executable binary

set(PROTOBUF_BIN_DIR "${Protobuf_LIB_DIRS}/../bin")
set(PROTOC_BIN_DIR "${ProtobufC_LIB_DIRS}/../bin")

find_program(PROTOC_EXECUTABLE protoc HINTS ${PROTOBUF_BIN_DIR})
find_program(PROTOC_GEN_C protoc-gen-c HINTS ${PROTOC_BIN_DIR})

message(STATUS "PROTOC_EXECUTABLE ${PROTOC_EXECUTABLE}")
message(STATUS "PROTOC_GEN_C ${PROTOC_GEN_C}")

set(PROTOBUFC_COMPILER ${PROTOC_EXECUTABLE})

# Usage:
# protobuf_generate_c(GEN_SOURCES GEN_INC_DIR myprotobuf.proto)
# add_executable(myexec ... ${GEN_SOURCES})
# target_include_directories(myexec ${GEN_INC_DIR})
function(protobuf_generate_c GEN_SRCS INC_DIR)
    if (NOT ARGN)
        message(SEND_ERROR "Error: PROTOC called without any proto files")
        return()
    endif (NOT ARGN)

    message(STATUS "PROTOC_EXECUTABLE ${PROTOC_EXECUTABLE}")
    message(STATUS "PROTOC_GEN_C ${PROTOC_GEN_C}")

    set(OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/protobuf_c_generated")
    file(MAKE_DIRECTORY ${OUTPUT_DIR})

    set(INCL)
    set(${GEN_SRCS})
    foreach (FIL ${ARGN})
        get_filename_component(ABS_FIL ${FIL} ABSOLUTE)
        get_filename_component(FIL_WE ${FIL} NAME_WE)
        list(APPEND ${GEN_SRCS} "${OUTPUT_DIR}/${FIL_WE}.pb-c.c")
        list(APPEND INCL "${OUTPUT_DIR}/${FIL_WE}.pb-c.h")

        message(STATUS "Running [${PROTOBUFC_COMPILER} --c_out ${OUTPUT_DIR} --plugin=${PROTOC_GEN_C} --proto_path ${CMAKE_CURRENT_SOURCE_DIR} ${FIL}]")

        add_custom_command(
            OUTPUT ${${GEN_SRCS}} ${INCL}
            COMMAND ${PROTOBUFC_COMPILER}
            ARGS --c_out ${OUTPUT_DIR} --plugin protoc-gen-c=${PROTOC_GEN_C} --proto_path ${CMAKE_CURRENT_SOURCE_DIR} ${FIL}
            DEPENDS ${ABS_FIL}
            COMMENT "Running [${PROTOBUFC_COMPILER} --c_out ${CMAKE_CURRENT_BINARY_DIR} --plugin protoc-gen-c=${PROTOC_GEN_C} --proto_path ${CMAKE_CURRENT_SOURCE_DIR} ${FIL}]"
            VERBATIM
        )
        set_source_files_properties(${${GEN_SRCS}} ${INCL} PROPERTIES GENERATED TRUE)
    endforeach (FIL)

    set(${GEN_SRCS} ${${GEN_SRCS}} PARENT_SCOPE)
    set(${INC_DIR} ${OUTPUT_DIR} PARENT_SCOPE)
endfunction()
