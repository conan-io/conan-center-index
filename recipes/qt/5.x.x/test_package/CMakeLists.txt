cmake_minimum_required(VERSION 3.1.0)

set(CMAKE_CXX_STANDARD 11)

project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_set_vs_runtime()
conan_set_libcxx()
conan_output_dirs_setup()

find_package(qt REQUIRED CONFIG)


set(SOURCES test_package.cpp)
qt5_wrap_cpp(SOURCES greeter.h)

qt5_add_resources(SOURCES example.qrc)

add_executable(${PROJECT_NAME} ${SOURCES})
# Must compile with "-fPIC" since Qt was built with -reduce-relocations.
target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)

target_link_libraries(${PROJECT_NAME} qt::qt)
