cmake_minimum_required(VERSION 3.15)

project(ironpress_conan_consumers LANGUAGES C CXX)

find_package(Ironpress REQUIRED CONFIG)

add_executable(ironpress_c_consumer src/c_consumer.c)
target_compile_features(ironpress_c_consumer PRIVATE c_std_11)
target_link_libraries(ironpress_c_consumer PRIVATE Ironpress::C)

add_executable(ironpress_cpp_consumer src/cpp_consumer.cpp)
target_compile_features(ironpress_cpp_consumer PRIVATE cxx_std_17)
target_link_libraries(ironpress_cpp_consumer PRIVATE Ironpress::CXX)
