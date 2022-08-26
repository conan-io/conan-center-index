cmake_minimum_required(VERSION 3.12)
project(Tixi-Conan-TestPackage)

find_package(tixi3 REQUIRED)

add_executable(tixi3_conan_test main.cpp)
target_link_libraries(tixi3_conan_test PRIVATE tixi3::tixi3)
