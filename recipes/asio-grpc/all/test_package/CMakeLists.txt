cmake_minimum_required(VERSION 3.14)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(asio-grpc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE asio-grpc::asio-grpc)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

# See https://github.com/chriskohlhoff/asio/issues/955
target_compile_definitions(${PROJECT_NAME}
                           PRIVATE BOOST_ASIO_DISABLE_STD_ALIGNED_ALLOC)

if(${asio-grpc_VERSION} VERSION_GREATER_EQUAL 2)
  target_compile_definitions(${PROJECT_NAME} PRIVATE ASIO_GRPC_V2)
endif()

if(CMAKE_CROSSCOMPILING)
  # Assuming protoc plugins needed by `asio_grpc_protobuf_generate` are not
  # available when cross compiling
  target_compile_definitions(${PROJECT_NAME} PRIVATE CROSSCOMPILING)
else()
  asio_grpc_protobuf_generate(
    GENERATE_GRPC
    TARGET
    ${PROJECT_NAME}
    OUT_DIR
    "${CMAKE_CURRENT_BINARY_DIR}/generated"
    PROTOS
    "${CMAKE_CURRENT_LIST_DIR}/test.proto")
endif()
