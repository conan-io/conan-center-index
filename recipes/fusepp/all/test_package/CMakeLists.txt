cmake_minimum_required(VERSION 3.1)
project(test_package)

include(FindPkgConfig)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

pkg_check_modules(FUSE REQUIRED fuse3)

add_executable(${PROJECT_NAME} hello.cpp helloFS.cpp)

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} ${FUSE_LIBRARIES})
target_include_directories(${PROJECT_NAME} PRIVATE ${FUSE_INCLUDE_DIRS})
