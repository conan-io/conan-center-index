cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper CXX)

find_package(Protobuf REQUIRED)
find_package(absl CONFIG REQUIRED)

add_subdirectory(src)

target_link_libraries(protobuf-mutator PUBLIC protobuf::libprotobuf absl::strings)
