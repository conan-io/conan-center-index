cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(BZip2 REQUIRED)
message("BZIP2_FOUND: ${BZIP2_FOUND}")
message("BZIP2_NEED_PREFIX: ${BZIP2_NEED_PREFIX}")
message("BZIP2_INCLUDE_DIRS: ${BZIP2_INCLUDE_DIRS}")
message("BZIP2_INCLUDE_DIR: ${BZIP2_INCLUDE_DIR}")
message("BZIP2_LIBRARIES: ${BZIP2_LIBRARIES}")
message("BZIP2_VERSION_STRING: ${BZIP2_VERSION_STRING}")

add_executable(test_package ../test_package/test_package.c)
target_link_libraries(test_package PRIVATE BZip2::BZip2)
