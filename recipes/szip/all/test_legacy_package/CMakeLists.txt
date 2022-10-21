cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(SZIP REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)

if(TARGET szip-shared)
   target_link_libraries(${PROJECT_NAME} szip-shared)
else ()
   target_link_libraries(${PROJECT_NAME} szip-static)
endif ()


if (NOT SZIP_FOUND)
   message (FATAL_ERROR "SZIP_FOUND should be set")
endif ()

add_executable("${PROJECT_NAME}-b" ../test_package/test_package.c)
 target_link_libraries("${PROJECT_NAME}-b" ${SZIP_LIBRARIES})
