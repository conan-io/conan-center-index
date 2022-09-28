cmake_minimum_required(VERSION 3.1)
project(test_package C)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GRAPHENE graphene-1.0)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ${GRAPHENE_LINK_LIBRARIES})
target_include_directories(${PROJECT_NAME} PRIVATE ${GRAPHENE_INCLUDE_DIRS})
