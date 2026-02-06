cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)
project(PackageTest CXX)

find_package(couchbase_cxx_client CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example couchbase_cxx_client::couchbase_cxx_client)
