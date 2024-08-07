list(PREPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR}/generators)

find_package(LZ4 REQUIRED CONFIG)
find_package(MySQL REQUIRED CONFIG)
#find_package(OpenSSL REQUIRED CONFIG)
find_package(Protobuf REQUIRED CONFIG)
find_package(RapidJSON REQUIRED CONFIG)
find_package(ZLIB REQUIRED CONFIG)
find_package(Zstd REQUIRED CONFIG)
