cmake_minimum_required(VERSION 3.5 FATAL_ERROR)
project("pkgtest_embree")

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# Build test executable:

add_executable(pkgtest_embree3 "${CMAKE_CURRENT_SOURCE_DIR}/pkg_test.cpp")
target_link_libraries(pkgtest_embree3 PRIVATE CONAN_PKG::embree3)

