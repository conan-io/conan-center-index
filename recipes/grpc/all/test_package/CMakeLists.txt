cmake_minimum_required(VERSION 3.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp helloworld.proto)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)  # grpc 1.47.0 requires c++14
target_link_libraries(${PROJECT_NAME}
    PRIVATE
        protobuf::libprotobuf
        $<IF:$<TARGET_EXISTS:gRPC::grpc++_unsecure>,gRPC::grpc++_unsecure,gRPC::grpc++>
)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
if(TEST_ACTUAL_SERVER)
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DTEST_ACTUAL_SERVER)
endif()
protobuf_generate(
    TARGET ${PROJECT_NAME}
    LANGUAGE cpp
)
protobuf_generate(
    TARGET ${PROJECT_NAME}
    LANGUAGE grpc
    GENERATE_EXTENSIONS .grpc.pb.h .grpc.pb.cc
    PLUGIN protoc-gen-grpc=$<TARGET_FILE:gRPC::grpc_cpp_plugin>
)
