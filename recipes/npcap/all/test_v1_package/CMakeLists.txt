cmake_minimum_required(VERSION 3.8)

project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(npcap REQUIRED CONFIG)

# Re-use the same source file from test_package folder
add_executable(${PROJECT_NAME} ../test_package/test_package.c)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE npcap::npcap)
