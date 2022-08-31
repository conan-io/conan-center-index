cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(charls CONFIG REQUIRED)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c PRIVATE charls)
set_target_properties(test_package_c PROPERTIES LINKER_LANGUAGE CXX)

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp PRIVATE charls)
target_compile_features(test_package_cpp PRIVATE cxx_std_14)
