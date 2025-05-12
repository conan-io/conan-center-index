cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(quickfast REQUIRED CONFIG)

add_executable(test ${PROJECT_SOURCE_DIR}/main.cpp)
target_link_libraries(test PRIVATE quickfast::quickfast)
target_compile_features(test PRIVATE cxx_std_11)
