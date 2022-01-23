cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Find Protobuf installation
set(protobuf_MODULE_COMPATIBLE TRUE)
find_package(protobuf CONFIG REQUIRED)
message(STATUS "Using protobuf ${protobuf_VERSION}")

# Find gRPC installation
find_package(gRPC CONFIG REQUIRED)
message(STATUS "Using gRPC ${gRPC_VERSION}")

# Proto file
get_filename_component(hw_proto "helloworld.proto" ABSOLUTE)
get_filename_component(hw_proto_path "${hw_proto}" PATH)

# Generated sources
set(hw_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.cc")
set(hw_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.h")
set(hw_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.cc")
set(hw_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.h")
add_custom_command(
    OUTPUT "${hw_proto_srcs}" "${hw_proto_hdrs}" "${hw_grpc_srcs}" "${hw_grpc_hdrs}"
    COMMAND $<TARGET_FILE:protobuf::protoc>
    ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
         --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
         -I "${hw_proto_path}"
         --plugin=protoc-gen-grpc="$<TARGET_FILE:gRPC::grpc_cpp_plugin>"
         "${hw_proto}"
    DEPENDS "${hw_proto}"
)

# Build generated sources as an object library
add_library(hw_proto_obj OBJECT ${hw_proto_srcs} ${hw_grpc_srcs})
target_include_directories(hw_proto_obj PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(hw_proto_obj PRIVATE gRPC::grpc protobuf::libprotobuf)
target_compile_features(hw_proto_obj PUBLIC cxx_std_11)

# Targets greeter_[async_](client)
add_executable(greeter_client_server greeter_client_server.cc)
target_link_libraries(greeter_client_server PRIVATE hw_proto_obj)
if(NOT SECURE)
    target_link_libraries(greeter_client_server PRIVATE gRPC::grpc++_unsecure)
else()
    target_link_libraries(greeter_client_server PRIVATE gRPC::grpc++)
endif()
