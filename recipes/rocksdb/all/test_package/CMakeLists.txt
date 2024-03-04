cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

enable_testing()

find_package(RocksDB REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_stable_abi test_package_stable_abi.cpp)
add_test(NAME ${PROJECT_NAME}_stable_abi COMMAND ${PROJECT_NAME}_stable_abi)
if(ROCKSDB_SHARED)
    target_link_libraries(${PROJECT_NAME}_stable_abi PRIVATE RocksDB::rocksdb-shared)
else()
    target_link_libraries(${PROJECT_NAME}_stable_abi PRIVATE RocksDB::rocksdb)

    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE RocksDB::rocksdb)
    if(RocksDB_VERSION VERSION_LESS "8.8.1")
        target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_11)
    else()
        target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_17)
    endif()
    add_test(NAME ${PROJECT_NAME}_cpp COMMAND ${PROJECT_NAME}_cpp)
endif()
