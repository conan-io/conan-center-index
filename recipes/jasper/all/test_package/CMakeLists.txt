cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Jasper REQUIRED)

message("JASPER_FOUND: ${JASPER_FOUND}")
message("JASPER_INCLUDE_DIR: ${JASPER_INCLUDE_DIR}")
message("JASPER_LIBRARIES: ${JASPER_LIBRARIES}")
message("JASPER_VERSION_STRING: ${JASPER_VERSION_STRING}")

add_executable(${PROJECT_NAME} test_package.c)
target_include_directories(${PROJECT_NAME} PRIVATE ${JASPER_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} ${JASPER_LIBRARIES})
