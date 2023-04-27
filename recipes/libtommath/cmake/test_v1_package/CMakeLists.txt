cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# workaround v1 legacy generators always haveing namespaces
add_library(libtommath)
target_link_libraries(libtommath libtommath::libtommath)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package/
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package/)
