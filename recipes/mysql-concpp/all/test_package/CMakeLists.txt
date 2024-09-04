cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(mysql-connector-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE mysql::concpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
