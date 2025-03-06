# Pre-find all dependencies, to prevent having to patch `find_dependency`
# which is included by Conan-generated CMake files, but also re-defined by the project itself

find_package(ZLIB REQUIRED CONFIG)
find_package(LZ4 REQUIRED CONFIG)
find_package(Zstd REQUIRED CONFIG)

find_package(RapidJSON REQUIRED CONFIG)
find_package(OpenSSL REQUIRED)

find_package(Protobuf REQUIRED CONFIG)
add_executable(ext::protoc ALIAS protobuf::protoc)
add_library(ext::protobuf-lite ALIAS protobuf::protobuf)


# This project will try combine all static libraries (and external dependencies)
# into a single library - mark all libraries from this project to limit
# the libraries that are combined
set(_CONAN_CMAKE_STATIC_LIBRARY_PREFIX_ORIG "${CMAKE_STATIC_LIBRARY_PREFIX}")
set(CMAKE_STATIC_LIBRARY_PREFIX "${CMAKE_STATIC_LIBRARY_PREFIX}_concpp_internal")


