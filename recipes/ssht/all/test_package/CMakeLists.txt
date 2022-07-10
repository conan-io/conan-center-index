cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Ssht REQUIRED NO_MODULE)

add_executable(${PROJECT_NAME} example.c)
target_compile_features(${PROJECT_NAME} PUBLIC c_std_99)
target_link_libraries(${PROJECT_NAME} ssht::ssht)
