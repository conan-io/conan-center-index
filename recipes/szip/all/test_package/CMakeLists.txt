cmake_minimum_required(VERSION 3.8)

project(test_package C)

find_package(szip REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} szip::szip)

# test the other target
add_executable("${PROJECT_NAME}-b" test_package.c)
if (BUILD_SHARED_LIBS)
   target_link_libraries("${PROJECT_NAME}-b" szip-shared)
else ()
   target_link_libraries("${PROJECT_NAME}-b" szip-static)
endif ()
