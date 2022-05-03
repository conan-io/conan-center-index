cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(QuaZip-Qt${QT_VERSION_MAJOR} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} QuaZip::QuaZip)
# Must compile with "-fPIC" since Qt was built with -reduce-relocations.
target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
