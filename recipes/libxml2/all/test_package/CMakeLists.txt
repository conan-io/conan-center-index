cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(LibXml2 REQUIRED)
message("LIBXML2_FOUND: ${LIBXML2_FOUND}")
message("LIBXML2_INCLUDE_DIR: ${LIBXML2_INCLUDE_DIR}")
message("LIBXML2_INCLUDE_DIRS: ${LIBXML2_INCLUDE_DIRS}")
message("LIBXML2_LIBRARIES: ${LIBXML2_LIBRARIES}")
message("LIBXML2_LIBRARY: ${LIBXML2_LIBRARY}")
message("LIBXML2_DEFINITIONS: ${LIBXML2_DEFINITIONS}")
message("LIBXML2_VERSION_STRING: ${LIBXML2_VERSION_STRING}")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} LibXml2::LibXml2)
