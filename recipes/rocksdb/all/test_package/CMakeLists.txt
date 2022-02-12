cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(RocksDB REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_stable_abi test_package_stable_abi.cpp)
if(ROCKSDB_SHARED)
  target_link_libraries(${PROJECT_NAME}_stable_abi RocksDB::rocksdb-shared)
else()
  target_link_libraries(${PROJECT_NAME}_stable_abi RocksDB::rocksdb)

  add_executable(${PROJECT_NAME}_cpp test_package.cpp)
  target_link_libraries(${PROJECT_NAME}_cpp RocksDB::rocksdb)
  set_property(TARGET ${PROJECT_NAME}_cpp PROPERTY CXX_STANDARD 11)
endif()
