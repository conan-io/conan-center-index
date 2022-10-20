cmake_minimum_required(VERSION 3.8)

project(test_package C)

find_package(SZIP REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET szip-shared)
    target_link_libraries(${PROJECT_NAME} szip-shared)
else ()
    target_link_libraries(${PROJECT_NAME} szip-static)
endif ()

if (NOT SZIP_FOUND)
   message (FATAL_ERROR "SZIP_FOUND should be set")
endif ()

add_executable("${PROJECT_NAME}-b" test_package.c)
target_link_libraries("${PROJECT_NAME}-b" ${SZIP_LIBRARIES})
