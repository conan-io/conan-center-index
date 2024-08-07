cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(sundials REQUIRED CONFIG)

# SUNDIALS v6.0.0 introduced a new SUNContext object on which all other SUNDIALS objects depend
# and is not backwards compatible.
if(sundials_VERSION GREATER_EQUAL 6)
    add_executable(${PROJECT_NAME} test_package_v6.c)
else()
    add_executable(${PROJECT_NAME} test_package_v5.c)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE sundials::sundials)
