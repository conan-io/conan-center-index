cmake_minimum_required(VERSION 3.15)
project(test_package CXX C)

find_package(TileDB REQUIRED CONFIG)

if (TILEDB_CPP_API)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE TileDB::tiledb)
    target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_17)
endif()

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE TileDB::tiledb)
target_compile_features(${PROJECT_NAME}_c PRIVATE c_std_99)
set_target_properties(${PROJECT_NAME}_c PROPERTIES LINKER_LANGUAGE CXX)
