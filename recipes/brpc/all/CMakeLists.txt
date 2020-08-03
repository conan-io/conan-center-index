cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# disable picking up system-installed libraries with find_library
set(CMAKE_FIND_USE_CMAKE_SYSTEM_PATH FALSE)

# we need to set the executable manually since that seems to be missing in
# the generated FindProtobuf.cmake in the protobuf conan package
find_program(PROTOBUF_PROTOC_EXECUTABLE NAMES protoc)
# the brpc build uses both variants of protobuf include directories
set(PROTOBUF_INCLUDE_DIRS "${CONAN_INCLUDE_DIRS_PROTOBUF}")
set(PROTOBUF_INCLUDE_DIR "${CONAN_INCLUDE_DIRS_PROTOBUF}")

find_package(OpenSSL REQUIRED)
set(OPENSSL_LIBRARIES OpenSSL::SSL)
set(OPENSSL_CRYPTO_LIBRARY OpenSSL::Crypto)

# this is used to select thrift debug vs release libraries in brpc's build
string(TOLOWER "${CMAKE_BUILD_TYPE}" RECIPE_BUILD_TYPE)

add_subdirectory(source_subfolder)
